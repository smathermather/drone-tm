/* eslint-disable jsx-a11y/interactive-supports-focus */
/* eslint-disable jsx-a11y/click-events-have-key-events */
import { useParams, useNavigate } from 'react-router-dom';
import { useTypedDispatch, useTypedSelector } from '@Store/hooks';
import { Flex } from '@Components/common/Layouts';
import Tab from '@Components/common/Tabs';
import {
  MapSection,
  Tasks,
  Instructions,
  Contributions,
} from '@Components/IndividualProject';
import { useGetProjectsDetailQuery } from '@Api/projects';
import { setProjectState } from '@Store/actions/project';
import { projectOptions } from '@Constants/index';
import hasErrorBoundary from '@Utils/hasErrorBoundary';

// function to render the content based on active tab
const getActiveTabContent = (
  activeTab: string,
  data: Record<string, any>,
  isProjectDataLoading: boolean,
) => {
  if (activeTab === 'tasks') return <Tasks />;
  if (activeTab === 'instructions')
    return (
      <Instructions
        projectData={data}
        isProjectDataLoading={isProjectDataLoading}
      />
    );
  if (activeTab === 'contributions') return <Contributions />;
  return <></>;
};

const IndividualProject = () => {
  const { id } = useParams();
  const dispatch = useTypedDispatch();
  const navigate = useNavigate();

  const individualProjectActiveTab = useTypedSelector(
    state => state.project.individualProjectActiveTab,
  );

  const { data: projectData, isLoading: isProjectDataLoading } =
    useGetProjectsDetailQuery(id as string, {
      onSuccess: (res: any) => {
        dispatch(
          setProjectState({
            // modify each task geojson and set locked user id and name to properties and save to redux state called taskData
            tasksData: res.tasks?.map((task: Record<string, any>) => ({
              ...task,
              outline_geojson: {
                ...task.outline_geojson,
                properties: {
                  ...task.outline_geojson.properties,
                  locked_user_id: task?.user_id,
                  locked_user_name: task?.name,
                },
              },
            })),
            projectArea: res.outline_geojson,
          }),
        );
      },
    });

  return (
    <section className="individual project naxatw-h-screen-nav naxatw-px-16 naxatw-py-8 xl:naxatw-px-20">
      {/* <----------- temporary breadcrumb -----------> */}
      <div className="breadcrumb naxatw-py-4">
        <span
          role="button"
          className="naxatw-cursor-pointer naxatw-text-body-md"
          onClick={() => {
            navigate('/projects');
          }}
        >
          Project /
        </span>
        <span className="naxatw-ml-1 naxatw-text-body-md naxatw-font-semibold">
          {
            // @ts-ignore
            projectData?.name || '--'
          }
        </span>
        {/* <----------- temporary breadcrumb -----------> */}
      </div>
      <Flex gap={5} className="naxatw-w-full !naxatw-flex-row">
        <div className="naxatw-h-[36.375rem] naxatw-w-[37.5%]">
          <Tab
            orientation="row"
            className="naxatw-bg-transparent hover:naxatw-border-b-2 hover:naxatw-border-red"
            activeClassName="naxatw-border-b-2 naxatw-bg-transparent naxatw-border-red"
            onTabChange={(val: any) =>
              dispatch(setProjectState({ individualProjectActiveTab: val }))
            }
            tabOptions={projectOptions}
            activeTab={individualProjectActiveTab}
            clickable
          />
          <div className="naxatw-h-[92.5%] naxatw-border-t">
            {getActiveTabContent(
              individualProjectActiveTab,
              projectData as Record<string, any>,
              isProjectDataLoading,
            )}
          </div>
        </div>
        <div className="!naxatw-max-h-[calc(100vh-17.375rem)] naxatw-w-[62.5%] naxatw-overflow-hidden naxatw-rounded-md">
          <MapSection />
        </div>
      </Flex>
    </section>
  );
};

export default hasErrorBoundary(IndividualProject);
