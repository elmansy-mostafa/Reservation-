document.addEventListener("DOMContentLoaded", () => {
  const departmentSelect = document.getElementById("department");
  const dateInput = document.getElementById("date");
  const slotSelect = document.getElementById("slot");
  const form = document.getElementById("booking-form");
  const messageDiv = document.getElementById("message");

  // Load available slots when department or date changes
  async function loadSlots() {
    const department = departmentSelect.value;
    const date = dateInput.value;

    slotSelect.innerHTML = '<option value="">Select…</option>';

    if (!department || !date) return;

    try {
      const response = await fetch(`/slots/available?department=${department}&date=${date}`);
      if (!response.ok) throw new Error("Error loading slots");

      const slots = await response.json();
      if (slots.length === 0) {
        const option = document.createElement("option");
        option.textContent = "No available slots";
        slotSelect.appendChild(option);
      } else {
        slots.forEach(slot => {
          const option = document.createElement("option");
          option.value = slot;
          option.textContent = slot;
          slotSelect.appendChild(option);
        });
      }
    } catch (err) {
      console.error(err);
      alert("Error fetching available slots. Please try again.");
    }
  }

  departmentSelect.addEventListener("change", loadSlots);
  dateInput.addEventListener("change", loadSlots);

  // Submit booking form
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const subject = document.getElementById("subject").value;
    const department = departmentSelect.value;
    const date = dateInput.value;
    const slot = slotSelect.value;

    try {
      const response = await fetch("/slots/book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, subject, department, date, slot }),
      });

      const result = await response.json();

      if (!response.ok) {
        messageDiv.textContent = result.detail || "Booking failed.";
        messageDiv.style.color = "red";
      } else {
        messageDiv.textContent = result.message;
        messageDiv.style.color = "green";
        loadSlots(); // Refresh available slots
        form.reset();
      }
    } catch (err) {
      console.error(err);
      messageDiv.textContent = "Booking error. Please try again.";
      messageDiv.style.color = "red";
    }
  });

  // Set date limits (26/04/2025 to 3 weeks ahead)
  const today = new Date("2025-04-26");
  const maxDate = new Date(today);
  maxDate.setDate(today.getDate() + 38);

  dateInput.min = today.toISOString().split("T")[0];
  dateInput.max = maxDate.toISOString().split("T")[0];
});
