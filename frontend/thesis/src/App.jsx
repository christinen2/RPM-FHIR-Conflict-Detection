import React, { useRef, useState } from "react";
import Banner from "./components/Banner";
import { Box } from "@mui/material";
import UploadBundlePage from "./pages/UploadBundlePage";
import EvaluatePage from "./pages/EvaluatePage";
import testBundle from "./test/testBundle.json";

function App() {
  // const [selectedFile, setSelectedFile] = useState(
  //   () =>
  //     new File([JSON.stringify(testBundle, null, 2)], "testBundle.json", {
  //       type: "application/json"
  //     })
  // ); // TEMP

  const [selectedFile, setSelectedFile] = useState(null); // TEMP

  const [stage, setStage] = useState(0);

  const nextStage = () => {
    setStage(stage + 1);
  };

  return (
    <Box
      sx={{
        height: "100vh",
        width: "100vw",
        overflowY: "hidden",
        display: "flex",
        alignItems: "center",
        flexDirection: "column"
      }}
    >
      <Banner onClick={() => setStage(0)} />
      {stage === 0 && (
        <UploadBundlePage
          selectedFile={selectedFile}
          setSelectedFile={setSelectedFile}
          nextStep={nextStage}
        />
      )}
      {stage == 1 && <EvaluatePage selectedFile={selectedFile} />}
    </Box>
  );
}

export default App;
