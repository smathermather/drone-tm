import { api, authenticated } from '.';

export const getTaskWaypoint = (projectId: string, taskId: string) =>
  authenticated(api).post(
    `/waypoint/task/${taskId}/?project_id=${projectId}&download=false`,
  );

export const getIndividualTask = (taskId: string) =>
  authenticated(api).get(`/tasks/${taskId}`);

export const postTaskWaypoint = (payload: Record<string, any>) => {
  const { taskId, projectId, data } = payload;
  return authenticated(api).post(
    `/waypoint/task/${taskId}/?project_id=${projectId}&download=false`,
    data,
    {
      headers: { 'Content-Type': 'application/json' },
    },
  );
};
