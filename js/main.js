(() => {
  document.documentElement.classList.add("js");

  // メニュー開閉（スマホ）
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  const setOpen = (open) => {
    toggle.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("is-open", open);
  };
  toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
  nav.addEventListener("click", (e) => { if (e.target.closest("a")) setOpen(false); });

  // ギャラリー拡大
  const lightbox = document.getElementById("lightbox");
  const lightboxImg = lightbox.querySelector("img");
  if (typeof lightbox.showModal === "function") {
    document.querySelectorAll(".gallery__item").forEach((item) => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        lightboxImg.src = item.getAttribute("href");
        lightboxImg.alt = item.querySelector("img").alt;
        lightbox.showModal();
      });
    });
    lightbox.addEventListener("click", (e) => {
      if (e.target === lightbox || e.target.closest(".lightbox__close")) lightbox.close();
    });
  }

  // 固定予約ボタン：ファーストビューと予約セクションが見えていない間だけ表示
  const cta = document.querySelector(".sticky-cta");
  const ctaLinks = cta.querySelectorAll("a");
  const visible = new Set();
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => (en.isIntersecting ? visible.add(en.target) : visible.delete(en.target)));
      const show = visible.size === 0;
      cta.classList.toggle("is-visible", show);
      cta.setAttribute("aria-hidden", String(!show));
      ctaLinks.forEach((a) => { a.tabIndex = show ? 0 : -1; });
    });
    [document.getElementById("top"), document.getElementById("contact")].forEach((el) => io.observe(el));
  }
})();
