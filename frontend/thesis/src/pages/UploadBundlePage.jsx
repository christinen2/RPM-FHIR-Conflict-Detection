import React, { useRef, useState } from "react";
import { Box, Button, Typography, Paper, Alert } from "@mui/material";
import CloudUploadOutlinedIcon from "@mui/icons-material/CloudUploadOutlined";
import InsertDriveFileOutlinedIcon from "@mui/icons-material/InsertDriveFileOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import PlayArrowRoundedIcon from "@mui/icons-material/PlayArrowRounded";

const UploadBundlePage = ({ selectedFile, setSelectedFile, nextStep }) => {
  const fileInputRef = useRef(null);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".json")) {
      setError("Please select a JSON file containing a FHIR Bundle.");
      event.target.value = "";
      return;
    }

    setError("");
    setSelectedFile(file);
  };

  const handleEvaluateBtnClick = () => {
    if (!selectedFile) {
      setError("Please upload a FHIR Bundle before evaluating.");
      return;
    }

    setError("");
    nextStep();
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100%",
        width: "100%",
        boxSizing: "border-box",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        p: { xs: 2, md: 4 },
        backgroundColor: "#F8FAFC"
      }}
    >
      <Box
        sx={{
          width: "100%",
          maxWidth: "620px",
          display: "flex",
          flexDirection: "column",
          gap: 3
        }}
      >
        <Box sx={{ textAlign: "center", mb: 1 }}>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              color: "#1E293B",
              letterSpacing: "-0.5px",
              mb: 1
            }}
          >
            Upload FHIR Bundle
          </Typography>
        </Box>

        {/* Upload panel */}
        <Paper
          elevation={0}
          sx={{
            p: { xs: 3, sm: 4 },
            border: "1px solid #E2E8F0",
            borderRadius: 3,
            backgroundColor: "#FFFFFF"
          }}
        >
          <Box
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();

              const file = event.dataTransfer.files?.[0];

              if (file) {
                if (!file.name.toLowerCase().endsWith(".json")) {
                  setError(
                    "Please select a JSON file containing a FHIR Bundle."
                  );
                  return;
                }

                setError("");
                setSelectedFile(file);
              }
            }}
            role="button"
            tabIndex={0}
            aria-label="Choose a FHIR Bundle JSON file"
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                fileInputRef.current?.click();
              }
            }}
            sx={{
              border: "2px dashed",
              borderColor: selectedFile ? "#93C5FD" : "#CBD5E1",
              borderRadius: 2,
              backgroundColor: selectedFile ? "#F0F7FF" : "#F8FAFC",
              p: { xs: 3, sm: 4 },
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center",
              cursor: "pointer",
              transition: "all 0.2s ease",
              "&:hover": {
                borderColor: "#2563EB",
                backgroundColor: "#EFF6FF"
              },
              "&:focus-visible": {
                outline: "2px solid #2563EB",
                outlineOffset: "3px"
              }
            }}
          >
            <Box
              sx={{
                width: 60,
                height: 60,
                borderRadius: 2,
                backgroundColor: selectedFile ? "#DBEAFE" : "#E2E8F0",
                color: selectedFile ? "#2563EB" : "#475569",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                mb: 2
              }}
            >
              {selectedFile ? (
                <InsertDriveFileOutlinedIcon sx={{ fontSize: 32 }} />
              ) : (
                <CloudUploadOutlinedIcon sx={{ fontSize: 32 }} />
              )}
            </Box>

            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                color: "#1E293B",
                mb: 1,
                overflowWrap: "anywhere"
              }}
            >
              {selectedFile ? selectedFile.name : "Upload your FHIR Bundle"}
            </Typography>

            <Typography variant="body2" sx={{ color: "#64748B", mb: 2 }}>
              {selectedFile
                ? `${(selectedFile.size / 1024).toFixed(1)} KB`
                : "Drag and drop your file here, or browse to choose a file"}
            </Typography>

            {!selectedFile && (
              <Typography
                variant="caption"
                sx={{
                  color: "#94A3B8",
                  display: "block"
                }}
              >
                Supported format: JSON (.json)
              </Typography>
            )}

            <input
              type="file"
              accept=".json,application/json"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: "none" }}
            />
          </Box>

          {error && (
            <Alert
              severity="error"
              sx={{ mt: 2, borderRadius: 2 }}
              onClose={() => setError("")}
            >
              {error}
            </Alert>
          )}

          {/* Selected file details */}
          {selectedFile && (
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1.5,
                mt: 2,
                p: 1.5,
                border: "1px solid #E2E8F0",
                borderRadius: 2
              }}
            >
              <InsertDriveFileOutlinedIcon sx={{ color: "#64748B" }} />

              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: "#334155",
                    overflowWrap: "anywhere"
                  }}
                >
                  {selectedFile.name}
                </Typography>

                <Typography variant="caption" sx={{ color: "#64748B" }}>
                  Ready for evaluation
                </Typography>
              </Box>

              <Button
                color="inherit"
                size="small"
                onClick={handleRemoveFile}
                aria-label="Remove selected file"
                startIcon={<DeleteOutlinedIcon />}
                sx={{ color: "#64748B", flexShrink: 0 }}
              >
                Remove
              </Button>
            </Box>
          )}

          <Box
            sx={{
              display: "flex",
              flexDirection: { xs: "column-reverse", sm: "row" },
              gap: 1.5,
              mt: 3
            }}
          >
            <Button
              variant="outlined"
              fullWidth
              onClick={() => fileInputRef.current?.click()}
              startIcon={<CloudUploadOutlinedIcon />}
              sx={{
                py: 1.25,
                borderColor: "#CBD5E1",
                color: "#334155",
                textTransform: "none",
                fontWeight: 600,
                borderRadius: 2,
                "&:hover": {
                  borderColor: "#94A3B8",
                  backgroundColor: "#F8FAFC"
                }
              }}
            >
              {selectedFile ? "Change File" : "Choose File"}
            </Button>

            <Button
              variant="contained"
              fullWidth
              onClick={handleEvaluateBtnClick}
              endIcon={<PlayArrowRoundedIcon />}
              sx={{
                py: 1.25,
                backgroundColor: "#2563EB",
                textTransform: "none",
                fontWeight: 600,
                borderRadius: 2,
                boxShadow: "none",
                "&:hover": {
                  backgroundColor: "#1D4ED8",
                  boxShadow: "0 4px 10px rgba(37, 99, 235, 0.2)"
                }
              }}
            >
              Evaluate Bundle
            </Button>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export default UploadBundlePage;
