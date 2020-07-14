import React from 'react';

const initialState = {
  relations: [
    {id: 108179, name: 'Дон', ref: 'М-4', type: 'road'},
  ],
};

const reducer = (state, action) => {
  switch (action.type) {
    case 'LOAD':
      return {
        ...state,
        relations: action.payload.elements.map(item => {
          return {
            id: item.id, 
            name: item.tags.name, 
            ref: item.tags.ref, 
            display_name: `${item.tags.ref} : ${item.tags.name}`, 
            type: 'road',}
        }).filter(x => x && x.ref && x.name).sort((x, y) => x.ref.localeCompare(y.ref))
      }

    default:
      return state;
  }
}

export const AppContext = React.createContext(initialState);
export const AppReducer = () => React.useReducer(reducer, initialState);

