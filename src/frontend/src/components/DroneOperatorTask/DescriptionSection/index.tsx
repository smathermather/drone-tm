/* eslint-disable no-nested-ternary */
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@Components/RadixComponents/Button';
import Tab from '@Components/common/Tabs';
import { useGetIndividualTaskQuery } from '@Api/tasks';
import { useTypedDispatch, useTypedSelector } from '@Store/hooks';
import { setSecondPageState } from '@Store/actions/droneOperatorTask';
import hasErrorBoundary from '@Utils/hasErrorBoundary';
import { toast } from 'react-toastify';
import UploadsBox from './UploadsBox';
import DescriptionBox from './DescriptionBox';

const { BASE_URL } = process.env;

const DroneOperatorDescriptionBox = () => {
  const { taskId, projectId } = useParams();
  const secondPageStates = useTypedSelector(state => state.droneOperatorTask);
  const { secondPageState, secondPage } = secondPageStates;
  const [animated, setAnimated] = useState(false);

  const { data: taskDescription }: Record<string, any> =
    useGetIndividualTaskQuery(taskId as string);

  useEffect(() => {
    setAnimated(true);
    setTimeout(() => {
      setAnimated(false);
    }, 100);
  }, [secondPageState, secondPage]);
  const variants = {
    open: { opacity: 1, y: 0 },
    closed: { opacity: 0, y: '50%' },
  };

  const renderComponent = (role: string) => {
    switch (role) {
      case 'description':
        return (
          <motion.div
            animate={animated ? 'closed' : 'open'}
            variants={{ ...variants }}
            className="naxatw-flex naxatw-w-full naxatw-flex-col naxatw-items-start naxatw-gap-5"
          >
            <DescriptionBox />
          </motion.div>
        );
      case 'uploads':
        return (
          <motion.div
            animate={animated ? 'closed' : 'open'}
            variants={{ ...variants }}
            className="naxatw-flex naxatw-w-full naxatw-flex-col naxatw-items-start naxatw-gap-5"
          >
            <UploadsBox />
          </motion.div>
        );
      default:
        return (
          <motion.div
            animate={animated ? 'closed' : 'open'}
            variants={{ ...variants }}
            className="naxatw-flex naxatw-w-full naxatw-flex-col naxatw-items-start naxatw-gap-5"
          >
            <DescriptionBox />
          </motion.div>
        );
    }
  };
  const dispatch = useTypedDispatch();

  const headerTabOptions = [
    {
      id: 1,
      label: 'Description',
      value: 'description',
    },
    {
      id: 2,
      label: 'Uploads',
      value: 'uploads',
    },
  ];

  const handleDownloadFlightPlan = () => {
    fetch(
      `${BASE_URL}/waypoint/task/${taskId}/?project_id=${projectId}&download=true`,
    )
      .then(response => {
        if (!response.ok) {
          throw new Error(`Network response was ${response.statusText}`);
        }
        return response.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        // link.setAttribute('download', '');
        link.href = url;
        link.download = 'flight_plan.kmz';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch(error =>
        toast.error(`There wan an error while downloading file
        ${error}`),
      );
  };

  return (
    <>
      <div className="naxatw-flex naxatw-w-full naxatw-flex-col naxatw-items-start naxatw-gap-3 lg:naxatw-gap-5">
        <div className="naxatw-flex naxatw-w-full naxatw-items-center naxatw-justify-between naxatw-self-stretch">
          <p className="naxatw-text-[0.875rem] naxatw-font-normal naxatw-leading-normal naxatw-text-[#484848]">
            Task #{taskDescription?.project_task_index}
          </p>
          <Button
            variant="ghost"
            className="naxatw-border naxatw-border-[#D73F3F] naxatw-text-[0.875rem] naxatw-text-[#D73F3F]"
            leftIcon="download"
            iconClassname="naxatw-text-[1.125rem]"
            onClick={() => handleDownloadFlightPlan()}
          >
            Download Flight Plan
          </Button>
        </div>
        <Tab
          onTabChange={value => {
            dispatch(setSecondPageState(value));
          }}
          tabOptions={headerTabOptions}
          activeTab={secondPageState}
          orientation="row"
          className={`naxatw-h-[3rem] naxatw-border-b naxatw-bg-transparent hover:naxatw-border-b-2 hover:naxatw-border-red ${!secondPage ? 'naxatw-hidden' : 'naxatw-block'}`}
          activeClassName="naxatw-border-b-2 naxatw-bg-transparent naxatw-border-red"
          clickable
        />
        {renderComponent(secondPageState)}
      </div>
    </>
  );
};

export default hasErrorBoundary(DroneOperatorDescriptionBox);
