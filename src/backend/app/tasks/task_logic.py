from psycopg import Connection
import uuid
from app.models.enums import HTTPStatus, State
from fastapi import HTTPException
from psycopg.rows import dict_row


async def update_notification(
    db: Connection,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    message: str,
):
    async with db.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO notifications (user_id, project_id, task_id, message,seen, created_at)
            VALUES (%(user_id)s, %(project_id)s, %(task_id)s, %(message)s,False, NOW())
            """,
            {
                "user_id": str(user_id),
                "project_id": project_id,
                "task_id": task_id,
                "message": message,
            },
        )
        return True


async def get_task_geojson(db: Connection, task_id: uuid.UUID):
    async with db.cursor() as cur:
        await cur.execute(
            """
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(outline)::jsonb,
                        'properties', jsonb_build_object(
                            'id', id
                        )
                    )
                )
            ) as geom
            FROM tasks
            WHERE id = %(task_id)s;
            """,
            {"task_id": str(task_id)},
        )

        data = await cur.fetchone()
        if data is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Task not found"
            )
        return data[0]
        # return json.loads(data[0]["geom"])


async def update_task_state(
    db: Connection,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    user_id: str,
    comment: str,
    initial_state: State,
    final_state: State,
):
    async with db.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            WITH last AS (
                SELECT *
                FROM task_events
                WHERE project_id = %(project_id)s AND task_id = %(task_id)s
                ORDER BY created_at DESC
                LIMIT 1
            ),
            locked AS (
                SELECT *
                FROM last
                WHERE user_id = %(user_id)s AND state = %(initial_state)s
            )
            INSERT INTO task_events(event_id, project_id, task_id, user_id, state, comment, created_at)
            SELECT gen_random_uuid(), project_id, task_id, user_id, %(final_state)s, %(comment)s, now()
            FROM last
            WHERE user_id = %(user_id)s
            RETURNING project_id, task_id, comment;
            """,
            {
                "project_id": str(project_id),
                "task_id": str(task_id),
                "user_id": str(user_id),
                "comment": comment,
                "initial_state": initial_state.name,
                "final_state": final_state.name,
            },
        )
        result = await cur.fetchone()
        return result


async def request_mapping(
    db: Connection,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    user_id: str,
    comment: str,
    initial_state: State,
    final_state: State,
):
    async with db.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            WITH last AS (
                SELECT *
                FROM task_events
                WHERE project_id= %(project_id)s AND task_id= %(task_id)s
                ORDER BY created_at DESC
                LIMIT 1
            ),
            released AS (
                SELECT COUNT(*) = 0 AS no_record
                FROM task_events
                WHERE project_id= %(project_id)s AND task_id= %(task_id)s AND state = %(unlocked_to_map_state)s
            )
            INSERT INTO task_events (event_id, project_id, task_id, user_id, comment, state, created_at)

            SELECT
                gen_random_uuid(),
                %(project_id)s,
                %(task_id)s,
                %(user_id)s,
                %(comment)s,
                %(request_for_map_state)s,
                now()
            FROM last
            RIGHT JOIN released ON true
            WHERE (last.state = %(unlocked_to_map_state)s OR released.no_record = true)
            RETURNING project_id, task_id, comment;
            """,
            {
                "project_id": str(project_id),
                "task_id": str(task_id),
                "user_id": str(user_id),
                "comment": comment,
                "unlocked_to_map_state": initial_state.name,  # State.UNLOCKED_TO_MAP.name,
                "request_for_map_state": final_state.name,  # State.REQUEST_FOR_MAPPING.name,
            },
        )
        result = await cur.fetchone()
        return result
