function createInfo() {

    const tooltip = document.createElement("div");
    tooltip.id = "tooltip"
    document.body.appendChild(tooltip);

    document.querySelectorAll(".tooltip-container").forEach(tipDiv => {

        tipDiv.addEventListener("mousemove", (e) => {
            tooltip.style.display = "block";
            tooltip.textContent = e.target.getAttribute("tooltip");
            tooltip.style.left = (e.pageX + 30) + "px";
            tooltip.style.top = e.pageY + "px";
        });

        tipDiv.addEventListener("mouseleave", () => {
            tooltip.style.display = "none";
        });
    });
}


if (document.readyState === "complete") createInfo()
else window.addEventListener("load", createInfo);
