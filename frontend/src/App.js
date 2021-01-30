import React from "react";
import { Provider } from "react-redux";
import { Router } from "react-router";
import { createBrowserHistory } from "history";
import { PersistGate } from "redux-persist/integration/react";

import MediaQuery from "containers/MediaQuery";
import Loading from "containers/Loading";

import Routes from "./routes";
import store, { persistor } from "./redux/store";

import config from "config";
import "./app.css";

const history = createBrowserHistory({ basename: config.BASE_URL });

function App() {
  return (
    <Router history={history}>
      <Provider store={store}>
        <PersistGate loading={null} persistor={persistor}>
          <Routes />
          <MediaQuery />
          <Loading />
        </PersistGate>
      </Provider>
    </Router>
  );
}

export default App;
