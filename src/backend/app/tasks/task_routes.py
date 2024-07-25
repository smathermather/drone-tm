import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from app.config import settings
from app.models.enums import EventType, State
from app.tasks import task_schemas, task_crud
from app.users.user_deps import login_required
from app.users.user_schemas import AuthUser
from app.users.user_crud import get_user_by_id
from databases import Database
from app.db import database
from app.utils import send_notification_email, render_email_template
from app.projects.project_crud import get_project_by_id


router = APIRouter(
    prefix=f"{settings.API_PREFIX}/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)


@router.get("/states/{project_id}")
async def task_states(
    project_id: uuid.UUID, db: Database = Depends(database.encode_db)
):
    """Get all tasks states for a project."""

    return await task_crud.all_tasks_states(db, project_id)


@router.post("/event/{project_id}/{task_id}")
async def new_event(
    background_tasks: BackgroundTasks,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    detail: task_schemas.NewEvent,
    user_data: AuthUser = Depends(login_required),
    db: Database = Depends(database.encode_db),
):
    user_id = user_data.id

    match detail.event:
        case EventType.REQUESTS:
            data = await task_crud.request_mapping(
                db,
                project_id,
                task_id,
                user_id,
                "Request for mapping",
            )

            # email notification
            project = await get_project_by_id(db, project_id)
            author = await get_user_by_id(db, project.author_id)

            html_content = render_email_template(
                template_name="mapping_requests.html",
                context={
                    "name": author.name,
                    "drone_operator_name": user_data.name,
                    "task_id": task_id,
                    "project_name": project.name,
                    "description": project.description,
                },
            )
            background_tasks.add_task(
                send_notification_email,
                user_data.email,
                "Request for mapping",
                html_content,
            )
            return data

        case EventType.MAP:
            project = await get_project_by_id(db, project_id)
            if user_id != project.author_id:
                raise HTTPException(
                    status_code=403,
                    detail="Only the project creator can approve the mapping.",
                )

            requested_user_id = await task_crud.get_requested_user_id(
                db, project_id, task_id
            )
            drone_operator = await get_user_by_id(db, requested_user_id)
            html_content = render_email_template(
                template_name="mapping_approved.html",
                context={
                    "email_subject": "Mapping Request Approved",
                    "email_body": "We are pleased to inform you that your mapping request has been approved. Your contribution is invaluable to our efforts in improving humanitarian responses worldwide.",
                    "task_status": "approved",
                    "name": user_data.name,
                    "drone_operator_name": drone_operator.name,
                    "task_id": task_id,
                    "project_name": project.name,
                    "description": project.description,
                },
            )

            background_tasks.add_task(
                send_notification_email,
                drone_operator.email_address,
                "Task is approved",
                html_content,
            )

            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                requested_user_id,
                "Request accepted for mapping",
                State.REQUEST_FOR_MAPPING,
                State.LOCKED_FOR_MAPPING,
            )

        case EventType.REJECTED:
            project = await get_project_by_id(db, project_id)
            if user_id != project.author_id:
                raise HTTPException(
                    status_code=403,
                    detail="Only the project creator can approve the mapping.",
                )

            requested_user_id = await task_crud.get_requested_user_id(
                db, project_id, task_id
            )
            drone_operator = await get_user_by_id(db, requested_user_id)
            html_content = render_email_template(
                template_name="mapping_approved.html",
                context={
                    "email_subject": "Mapping Request Rejected",
                    "email_body": "We are sorry to inform you that your mapping request has been rejected.",
                    "task_status": "rejected",
                    "name": user_data.name,
                    "drone_operator_name": drone_operator.name,
                    "task_id": task_id,
                    "project_name": project.name,
                    "description": project.description,
                },
            )

            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                requested_user_id,
                "Request for mapping rejected",
                State.REQUEST_FOR_MAPPING,
                State.UNLOCKED_TO_MAP,
            )
        case EventType.FINISH:
            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                user_id,
                "Done: unlocked to validate",
                State.LOCKED_FOR_MAPPING,
                State.UNLOCKED_TO_VALIDATE,
            )
        case EventType.VALIDATE:
            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                user_id,
                "Done: locked for validation",
                State.UNLOCKED_TO_VALIDATE,
                State.LOCKED_FOR_VALIDATION,
            )
        case EventType.GOOD:
            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                user_id,
                "Done: Task is Good",
                State.LOCKED_FOR_VALIDATION,
                State.UNLOCKED_DONE,
            )

        case EventType.BAD:
            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                user_id,
                "Done: needs to redo",
                State.LOCKED_FOR_VALIDATION,
                State.UNLOCKED_TO_MAP,
            )

    return True


@router.get("/requested_tasks/{project_id}/pending")
async def get_pending_tasks(
    project_id: uuid.UUID,
    user_data: AuthUser = Depends(login_required),
    db: Database = Depends(database.encode_db),
):
    """Get a list of pending tasks for a specific project and user."""
    user_id = user_data.id

    pending_tasks = await task_crud.get_project_task_by_id(db, project_id, user_id)
    if pending_tasks is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return pending_tasks
