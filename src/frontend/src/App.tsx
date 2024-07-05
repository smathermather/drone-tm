import { useLocation } from 'react-router-dom';
import { initDomToCode } from 'dom-to-code';
import { ToastContainer } from 'react-toastify';
import { useTypedDispatch, useTypedSelector } from '@Store/hooks';
import generateRoutes from '@Routes/generateRoutes';
import appRoutes from '@Routes/appRoutes';
import testRoutes from '@Routes/testRoutes';
import {
  setModalContent,
  setPromptDialogContent,
  toggleModal,
  togglePromptDialog,
} from '@Store/actions/common';
import 'react-toastify/dist/ReactToastify.css';
import Modal from '@Components/common/Modal';
import Navbar from '@Components/common/Navbar';
import PromptDialog from '@Components/common/PromptDialog';
import {
  getModalContent,
  getPromptDialogContent,
} from '@Constants/modalContents';

export default function App() {
  const dispatch = useTypedDispatch();
  const { pathname } = useLocation();
  const showModal = useTypedSelector(state => state.common.showModal);
  const modalContent = useTypedSelector(state => state.common.modalContent);
  const showPromptDialog = useTypedSelector(
    state => state.common.showPromptDialog,
  );
  const promptDialogContent = useTypedSelector(
    state => state.common.promptDialogContent,
  );

  const handleModalClose = () => {
    dispatch(toggleModal());
    setTimeout(() => {
      dispatch(setModalContent(null));
    }, 150);
  };

  const handlePromptDialogClose = () => {
    dispatch(togglePromptDialog());
    setTimeout(() => {
      dispatch(setPromptDialogContent(null));
    }, 150);
  };

  // add routes where you dont want navigation bar
  const routesWithoutNavbar = ['/login', '/'];

  return (
    <>
      {process.env.NODE_ENV !== 'production' &&
        !process.env.DISABLE_DOM_TO_CODE &&
        initDomToCode()}
      <div>
        <ToastContainer />

        {!routesWithoutNavbar.includes(pathname) && <Navbar />}

        <Modal
          show={showModal}
          className={getModalContent(modalContent)?.className || ''}
          title={getModalContent(modalContent)?.title}
          onClose={handleModalClose}
          hideCloseButton={!!getModalContent(modalContent)?.hideCloseButton}
        >
          {getModalContent(modalContent)?.content}
        </Modal>

        <PromptDialog
          show={showPromptDialog}
          title={getPromptDialogContent(promptDialogContent)?.title}
          onClose={handlePromptDialogClose}
        >
          {getPromptDialogContent(promptDialogContent)?.content}
        </PromptDialog>

        {generateRoutes({
          routes:
            process.env.NODE_ENV !== 'production'
              ? [...testRoutes, ...appRoutes]
              : appRoutes,
        })}
      </div>
    </>
  );
}
