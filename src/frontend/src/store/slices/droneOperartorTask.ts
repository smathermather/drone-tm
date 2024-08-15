/* eslint-disable no-param-reassign */
import { createSlice } from '@reduxjs/toolkit';

export interface IDroneOperatorTaskState {
  secondPage: boolean;
  secondPageState: string;
  clickedImage: string;
  checkedImages: Record<number, boolean>;
  popOver: boolean;
}

const initialState: IDroneOperatorTaskState = {
  secondPage: false,
  secondPageState: 'description',
  clickedImage: '',
  checkedImages: {},
  popOver: false,
};

export const droneOperatorTaskSlice = createSlice({
  name: 'droneOperatorTask',
  initialState,
  reducers: {
    setSecondPage: (state, action) => {
      state.secondPage = action.payload;
    },
    setSecondPageState: (state, action) => {
      state.secondPageState = action.payload;
    },
    setSelectedImage: (state, action) => {
      state.clickedImage = action.payload;
    },
    setCheckedImages: (state, action) => {
      state.checkedImages = action.payload;
    },
    unCheckImages: (state, action) => {
      state.checkedImages[action.payload] =
        !state.checkedImages[action.payload];
    },
    showPopover: state => {
      state.popOver = !state.popOver;
    },
    unCheckAllImages: state => {
      Object.keys(state.checkedImages).forEach((key: any) => {
        state.checkedImages[key] = false;
      });
    },
    checkAllImages: state => {
      Object.keys(state.checkedImages).forEach((key: any) => {
        state.checkedImages[key] = true;
      });
    },
  },
});

export default droneOperatorTaskSlice.reducer;