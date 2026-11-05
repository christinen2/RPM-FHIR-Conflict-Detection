// const API = "http://127.0.0.1:5500";
const API = "";

export const findConflicts = async (selectedFile) => {
  const fileText = await selectedFile.text();
  const payload = JSON.parse(fileText);

  try {
    const res = await fetch(`${API}/api/detect-conflicts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      throw new Error(`HTTP error! Status: ${res.status}`);
    }

    const result = await res.json();
    return result;
  } catch (error) {
    console.error("Error calling API:", error);
    throw error;
  }
};

export const countResources = async (selectedFile) => {
  const fileText = await selectedFile.text();
  const payload = JSON.parse(fileText);

  try {
    const res = await fetch(`${API}/api/count-resources`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`HTTP error! Status: ${res.status}`);
    }

    const result = await res.json();
    return result;
  } catch (error) {
    console.error("Error calling API:", error);
    throw error;
  }
};
