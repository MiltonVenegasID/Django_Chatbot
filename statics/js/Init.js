document.addEventListener("scroll", function () {
    let scrollPosition = window.scrollY;

    const parallaxElements = document.querySelectorAll("[data-speed]");

    parallaxElements.forEach((element) => {
        let speed = element.getAttribute("data-speed");

        element.style.transform = `translateY(${scrollPosition * speed}px)`;
    });
});
AOS.init();