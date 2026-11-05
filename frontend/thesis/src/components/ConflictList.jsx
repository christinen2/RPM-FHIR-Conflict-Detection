import React, { useEffect, useState } from "react";
import { Box, Container, Typography } from "@mui/material";
import Section from "./Section";
import ConflictCard from "./ConflictCard";

const ConflictList = ({ res }) => {
  const [listConflicts, setListConflicts] = useState([]);
  useEffect(() => {
    if (!res || !res.conflicts) {
      setListConflicts([]);
      return;
    }

    setListConflicts(
      res.conflicts.map((conflict, index) => (
        <ConflictCard key={index} index={index} conflict={conflict} />
      ))
    );
  }, [res]);

  return (
    <Section>
      {listConflicts.length === 0 ? "No conflicts found." : listConflicts}
    </Section>
  );
};

export default ConflictList;
