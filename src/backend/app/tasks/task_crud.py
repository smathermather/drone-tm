import uuid
from databases import Database
from app.models.enums import State


async def get_all_tasks(db: Database, project_id: uuid.UUID):
    query = """
        SELECT id FROM tasks WHERE project_id = :project_id
    """
    values = {"project_id": str(project_id)}

    data = await db.fetch_all(query, values)

    # Extracting the list of IDs from the data
    task_ids = [task["id"] for task in data]

    return task_ids


async def all_tasks_states(db: Database, project_id: uuid.UUID):
    query = """
        SELECT DISTINCT ON (task_id) project_id, task_id, state
        FROM task_events
        WHERE project_id = :project_id
        ORDER BY task_id, created_at DESC
    """

    r = await db.fetch_all(query, {"project_id": str(project_id)})

    # Extract task_ids and corresponding states from the query result
    existing_tasks = [dict(r) for r in r]

    # Get all task_ids from the tasks table
    task_ids = await get_all_tasks(db, project_id)

    # Create a set of existing task_ids for quick lookup
    existing_task_ids = {task["task_id"] for task in existing_tasks}

    # task ids that are not in task_events table
    remaining_task_ids = [x for x in task_ids if x not in existing_task_ids]

    # Add missing tasks with state as "UNLOCKED_FOR_MAPPING"
    remaining_tasks = [
        {
            "project_id": str(project_id),
            "task_id": task_id,
            "state": State.UNLOCKED_TO_MAP.name,
        }
        for task_id in remaining_task_ids
    ]

    # Combine both existing tasks and remaining tasks
    combined_tasks = existing_tasks + remaining_tasks

    return combined_tasks


async def request_mapping(
    db: Database, project_id: uuid.UUID, task_id: uuid.UUID, user_id: str, comment: str
):
    query = """
            WITH last AS (
                SELECT *
                FROM task_events
                WHERE project_id= :project_id AND task_id= :task_id
                ORDER BY created_at DESC
                LIMIT 1
            ),
            released AS (
                SELECT COUNT(*) = 0 AS no_record
                FROM task_events
                WHERE project_id= :project_id AND task_id= :task_id AND state = :unlocked_to_map_state
            )
            INSERT INTO task_events (event_id, project_id, task_id, user_id, comment, state, created_at)

            SELECT
                gen_random_uuid(),
                :project_id,
                :task_id,
                :user_id,
                :comment,
                :request_for_map_state,
                now()
            FROM last
            RIGHT JOIN released ON true
            WHERE (last.state = :unlocked_to_map_state OR released.no_record = true);
            """

    values = {
        "project_id": str(project_id),
        "task_id": str(task_id),
        "user_id": str(user_id),
        "comment": comment,
        "unlocked_to_map_state": State.UNLOCKED_TO_MAP.name,
        "request_for_map_state": State.REQUEST_FOR_MAPPING.name,
    }

    await db.fetch_one(query, values)

    return {"project_id": project_id, "task_id": task_id, "comment": comment}


async def update_task_state(
    db: Database,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    user_id: str,
    comment: str,
    initial_state: State,
    final_state: State,
):
    query = """
                WITH last AS (
                    SELECT *
                    FROM task_events
                    WHERE project_id = :project_id AND task_id = :task_id
                    ORDER BY created_at DESC
                    LIMIT 1
                ),
                locked AS (
                    SELECT *
                    FROM last
                    WHERE user_id = :user_id AND state = :initial_state
                )
                INSERT INTO task_events(event_id, project_id, task_id, user_id, state, comment, created_at)
                SELECT gen_random_uuid(), project_id, task_id, user_id, :final_state, :comment, now()
                FROM last
                WHERE user_id = :user_id
                RETURNING project_id, task_id, user_id, state;
        """

    values = {
        "project_id": str(project_id),
        "task_id": str(task_id),
        "user_id": str(user_id),
        "comment": comment,
        "initial_state": initial_state.name,
        "final_state": final_state.name,
    }

    await db.fetch_one(query, values)

    return {"project_id": project_id, "task_id": task_id, "comment": comment}


async def get_requested_user_id(
    db: Database, project_id: uuid.UUID, task_id: uuid.UUID
):
    query = """
        SELECT user_id
        FROM task_events
        WHERE project_id = :project_id AND task_id = :task_id and state = :request_for_map_state
        ORDER BY created_at DESC
        LIMIT 1
        """
    values = {
        "project_id": str(project_id),
        "task_id": str(task_id),
        "request_for_map_state": State.REQUEST_FOR_MAPPING.name,
    }

    result = await db.fetch_one(query, values)
    if result is None:
        raise ValueError("No user requested for mapping")
    return result["user_id"]