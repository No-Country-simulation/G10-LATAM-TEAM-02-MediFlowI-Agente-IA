export const formatDate = (dateInput) => {
  if (!dateInput) return "No identificado";
  try {
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) {
      return String(dateInput);
    }
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");

    return `${day}/${month}/${year} ${hours}:${minutes}`;
  } catch (error) {
    return String(dateInput);
  }
};

export const formatDateShort = (dateInput) => {
  if (!dateInput) return "No identificado";
  try {
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) {
      return String(dateInput);
    }
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();

    return `${day}/${month}/${year}`;
  } catch (error) {
    return String(dateInput);
  }
};
