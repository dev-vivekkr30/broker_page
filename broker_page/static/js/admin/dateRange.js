$(document).ready(function () {
    let dropdownBtn = $("#dropdown-btn");

    // Set default value to the current date
    dropdownBtn.text(moment().format("MMMM D, YYYY"));

    // Function to update dropdown button text
    $(".dropdown-item").click(function () {
        let selectedValue = $(this).data("value");

        if (selectedValue) {
            let dateText = getDateRange(selectedValue);
            dropdownBtn.text(dateText);
        } else if ($(this).hasClass("custom-date")) {
            openDateRangePicker();
        }
    });

    // Function to get date range based on selection
    function getDateRange(option) {
        let today = moment();
        switch (option) {
            case "Today":
                return today.format("MMMM D, YYYY");
            case "This Week":
                return today.startOf("isoWeek").format("MMM D") + " - " + today.endOf("isoWeek").format("MMM D, YYYY");
            case "This Month":
                return today.startOf("month").format("MMM D") + " - " + today.endOf("month").format("MMM D, YYYY");
            case "This Quarter":
                return today.startOf("quarter").format("MMM D") + " - " + today.endOf("quarter").format("MMM D, YYYY");
            case "This Year":
                return today.startOf("year").format("MMM D") + " - " + today.endOf("year").format("MMM D, YYYY");
            default:
                return today.format("MMMM D, YYYY");
        }
    }

    // Function to open date range picker
    function openDateRangePicker() {
        let start = moment().startOf("month");
        let end = moment().endOf("month");

        let $input = $("<input type='text' id='daterange-picker' style='position:absolute;opacity:0;'>")
            .appendTo("body")
            .daterangepicker({
                startDate: start,
                endDate: end,
                opens: "center",
                autoUpdateInput: false
            }, function (start, end) {
                dropdownBtn.text(start.format("MMM D") + " - " + end.format("MMM D, YYYY"));
            })
            .trigger("click");

        // Close picker and remove input after Apply button is clicked
        $input.on("apply.daterangepicker", function (ev, picker) {
            picker.hide();
            $input.remove();
        });

        // Close picker and remove input if canceled
        $input.on("cancel.daterangepicker", function (ev, picker) {
            picker.hide();
            $input.remove();
        });
    }
});


// Reset button feature
function resetFilters(event) {
    event.preventDefault();

    // Reset State Dropdown
    const stateSelect = document.getElementById("state");
    if (stateSelect) {
        stateSelect.value = "All";
    }

    // Reset City Dropdown
    const citySelect = document.getElementById("city");
    if (citySelect) {
        citySelect.value = "All";
    }

    // Reset Date Dropdown Button
    const dateDropdownBtn = document.getElementById("dropdown-btn");
    if (dateDropdownBtn) {
        dateDropdownBtn.textContent = "Select Date";
    }
}
