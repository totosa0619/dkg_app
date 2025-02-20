import { CircularProgress } from "@mui/material";
import React, { useState, Suspense, useEffect } from "react";

function LazyComponent({ componentName, data, isEditMode }) {
  const [SelectedComponent, setSelectedComponent] = useState(null);

  useEffect(() => {
    setSelectedComponent(null);
    let Component;
    try {
      Component = React.lazy(() => import(`../${componentName}/index.jsx`));
    } catch (e) {
      Component = React.lazy(() => import(`../${componentName}/${componentName}.jsx`));
    }

    if (!Component) {
      console.error("could not load", componentName)
    }
    setSelectedComponent(Component);
  }, [componentName]);

  return (
    <>
      {SelectedComponent && (
        <Suspense fallback={<CircularProgress />}>
          <SelectedComponent
            key={`${componentName}`}
            data={data}
            geoDashboard={true}
            isEditMode={isEditMode}
          />
        </Suspense>
      )}
    </>
  );
}

export default LazyComponent;
