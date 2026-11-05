import React, { useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";

import SyntaxHighlighter from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";

import Section from "./Section";

const FhirCodeBlock = ({ selectedFile }) => {
  const [fileContent, setFileContent] = useState("");

  useEffect(() => {
    if (!selectedFile) {
      setFileContent("");
      return;
    }

    selectedFile.text().then((text) => {
      try {
        const formatted = JSON.stringify(JSON.parse(text), null, 2);
        setFileContent(formatted);
      } catch {
        setFileContent(text);
      }
    });
  }, [selectedFile]);

  return (
    <Section header={selectedFile ? selectedFile.name : "FHIR Bundle"}>
      <Box>
        <SyntaxHighlighter
          language="json"
          style={oneLight}
          showLineNumbers
          wrapLongLines
          customStyle={{
            background: "transparent",
            backgroundColor: "transparent",
            padding: 0,
            margin: "0 0 0 -1.3rem",
            fontSize: "13px"
          }}
          codeTagProps={{
            style: {
              background: "transparent",
              backgroundColor: "transparent"
            }
          }}
        >
          {fileContent}
        </SyntaxHighlighter>
      </Box>
    </Section>
  );
};

export default FhirCodeBlock;
