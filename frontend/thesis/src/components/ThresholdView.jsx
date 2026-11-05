import React, { useEffect, useState } from "react";
import { Box, Container, Typography } from "@mui/material";
import Section from "./Section";
import ConflictCard from "./ConflictCard";
import RangeVisualisation from "./RangeVisualisation";

const ThresholdView = ({ res }) => {
  const [listConflicts, setListConflicts] = useState([]);
  useEffect(() => {
    if (!res || !res.conflicts) {
      setListConflicts([]);
      return;
    }

    setListConflicts(
      res.conflicts.map((conflict, index) => (
        <RangeVisualisation key={index} conflict={conflict} />
      ))
    );
  }, [res]);

  return <Section>{listConflicts}</Section>;
};

export default ThresholdView;
