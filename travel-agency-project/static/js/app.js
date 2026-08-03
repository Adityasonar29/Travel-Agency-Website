/* ═══════════════════════════════════════════════════════════════
   VOYAGE — Updated Main JavaScript
   Snap scroll · Filled cursor · Infinite drag · Map animation
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    gsap.registerPlugin(ScrollTrigger);
    initSmoothScroll();
    initCustomCursor();
    initNavbar();
    initMenuOverlay();
    initScrollProgress();
    initHeroAnimations();
    initDestinationPage();
    initImageReveal();
    initRiseCards();
    initStatCounters();
    initInfiniteDrag();
    initTestimonialCarousel();
    initZoomScroll();
    initScrollReveal();
    initMapAnimation();
    initBigTextParallax();

    // Loading screen only if present (home page first load)
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        initLoadingScreen();
    } else {
        const main = document.getElementById('main-content');
        if (main) main.style.opacity = '1';
    }
});

/* ═══════════════════════════════════════════
   SMOOTH SCROLL (Lenis) — Ultra smooth
   ═══════════════════════════════════════════ */
function initSmoothScroll() {
    const lenis = new Lenis({
        duration: 1.6,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        smoothWheel: true,
        wheelMultiplier: 0.8,
        touchMultiplier: 1.5,
    });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
    window.lenis = lenis;
}

/* ═══════════════════════════════════════════
   LOADING SCREEN (Only home page)
   ═══════════════════════════════════════════ */
function initLoadingScreen() {
    const screen = document.getElementById('loading-screen');
    const cards = document.querySelectorAll('.deck-card');
    const logo = document.getElementById('loading-logo');
    const logoLine = document.getElementById('logo-line');
    const logoSub = document.getElementById('logo-sub');
    const mainContent = document.getElementById('main-content');

    const tl = gsap.timeline({
        onComplete: () => {
            gsap.to(screen, {
                yPercent: -100, duration: 0.8, ease: 'power4.inOut',
                onComplete: () => {
                    screen.style.display = 'none';
                    if (mainContent) mainContent.style.opacity = '1';
                    triggerHeroAnimations();
                }
            });
        }
    });

    cards.forEach((card, i) => {
        tl.to(card, {
            opacity: 1, rotation: (i - 2) * 8, x: (i - 2) * 50, y: (i - 2) * 30,
            scale: 0.85, zIndex: cards.length - i, duration: 0.6, ease: 'power3.out',
        }, i * 0.12);
    });
    tl.to('.deck-card', { x: 0, y: 0, rotation: 0, scale: 1, duration: 0.8, ease: 'power3.inOut', stagger: { each: 0.05, from: 'end' } }, '+=0.5');
    tl.to('.deck-card', { scale: 0, opacity: 0, duration: 0.5, ease: 'power3.in', stagger: { each: 0.04, from: 'center' } }, '+=0.3');
    tl.to(logo, { opacity: 1, duration: 0.1 }, '-=0.2');
    tl.to(logoLine, { width: 120, duration: 0.6, ease: 'power2.out' }, '-=0.1');
    tl.to(logoSub, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }, '-=0.3');
    tl.to({}, { duration: 0.8 });
}

/* ═══════════════════════════════════════════
   HERO ANIMATIONS
   ═══════════════════════════════════════════ */
function initHeroAnimations() {
    const hero = document.getElementById('hero');
    if (!hero) return;
    hero.addEventListener('mousemove', (e) => {
        const x = (e.clientX / window.innerWidth - 0.5) * 2;
        const y = (e.clientY / window.innerHeight - 0.5) * 2;
        document.querySelectorAll('.parallax-layer').forEach((layer) => {
            const speed = parseFloat(layer.dataset.speed) || -0.3;
            gsap.to(layer, { x: x * speed * 40, y: y * speed * 30, duration: 1.2, ease: 'power2.out' });
        });
    });
}

function triggerHeroAnimations() {
    const tl = gsap.timeline({ delay: 0.3 });
    tl.to('.hero-fade', { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out', stagger: 0.3 });
    tl.to('.hero-clip', { clipPath: 'inset(0% 0 0 0)', y: 0, duration: 1.5, ease: 'power3.out', stagger: 0.3 }, '-=1.2');
}

function initDestinationPage() {
    const heroSection = document.getElementById('destination-hero');
    const heroParallax = document.querySelector('.hero-parallax');

    if (heroSection && heroParallax) {
        ScrollTrigger.create({
            trigger: heroSection,
            start: 'top top',
            end: 'bottom top',
            scrub: true,
            onUpdate: (self) => {
                heroParallax.style.transform = `translateY(${self.progress * 35}%)`;
            },
        });
    }
}

/* ═══════════════════════════════════════════
   CUSTOM CURSOR — Filled inversion circle
   ═══════════════════════════════════════════ */
function initCustomCursor() {
    const ring = document.getElementById('cursor-ring');
    const dot = document.getElementById('cursor-dot');
    if (!ring || !dot || window.innerWidth < 768) return;

    document.body.style.cursor = 'none';

    window.addEventListener('mousemove', (e) => {
        gsap.to(ring, { x: e.clientX, y: e.clientY, duration: 0.5, ease: 'power2.out' });
        gsap.to(dot, { x: e.clientX, y: e.clientY, duration: 0.1 });
    });

    // Expand on interactive elements
    document.querySelectorAll('a, button, [data-cursor-hover], .rise-card, .drag-card').forEach((el) => {
        el.addEventListener('mouseenter', () => {
            ring.style.width = '70px'; ring.style.height = '70px';
            ring.style.marginLeft = '-35px'; ring.style.marginTop = '-35px';
            ring.style.opacity = '0.6';
        });
        el.addEventListener('mouseleave', () => {
            ring.style.width = '40px'; ring.style.height = '40px';
            ring.style.marginLeft = '-20px'; ring.style.marginTop = '-20px';
            ring.style.opacity = '0.85';
        });
    });
}

/* ═══════════════════════════════════════════
   NAVBAR — Scroll hide/show, direction-aware
   ═══════════════════════════════════════════ */
function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    let lastScrollY = window.scrollY;
    let ticking = false;

    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const currentScrollY = window.scrollY;
                const delta = currentScrollY > lastScrollY ? 1 : -1;
                const navbarHeight = navbar.offsetHeight;

                // Smooth scroll handling
                if (delta > 0) {
                    // Scrolling down - hide
                    if (currentScrollY > navbarHeight) {
                        navbar.classList.remove('navbar-appearing', 'navbar-revealing');
                        navbar.classList.add('navbar-hidden');
                        navbar.classList.add('navbar-revealing');
                        navbar.style.transform = `translateY(-${navbarHeight}px)`;
                    }
                } else {
                    // Scrolling up - show
                    navbar.classList.remove('navbar-hidden', 'navbar-revealing');
                    navbar.classList.add('navbar-appearing');
                    navbar.classList.add('navbar-revealing');
                    navbar.style.transform = 'translateY(0)';
                }

                // Update last scroll position
                lastScrollY = currentScrollY > 0 ? currentScrollY : 0;
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });

    // Handle first load and resize
    window.addEventListener('resize', () => {
        navbar.style.transform = navbar.classList.contains('navbar-hidden') ? `translateY(-${navbar.offsetHeight}px)` : 'translateY(0)';
    });

    // Initial check
    if (window.scrollY > navbar.offsetHeight) {
        navbar.classList.add('navbar-hidden');
    }
}

/* ═══════════════════════════════════════════
   MENU OVERLAY — Full-screen nav
   ═══════════════════════════════════════════ */
function initMenuOverlay() {
    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const overlay = document.getElementById('menu-overlay');
            if (overlay && overlay.classList.contains('active')) toggleMenu();
        }
    });
}

function toggleMenu() {
    const overlay = document.getElementById('menu-overlay');
    const btn = document.getElementById('mobile-menu-btn');
    const links = document.querySelectorAll('.menu-link');

    if (!overlay) return;

    const isActive = overlay.classList.contains('active');

    if (isActive) {
        // Close
        overlay.classList.remove('active');
        btn.classList.remove('active');
        links.forEach((l, i) => {
            l.style.transitionDelay = `${i * 0.05}s`;
            l.style.opacity = '0';
            l.style.transform = 'translateY(30px)';
        });
    } else {
        // Open
        overlay.classList.add('active');
        btn.classList.add('active');
        links.forEach((l, i) => {
            l.style.transitionDelay = `${0.2 + i * 0.08}s`;
            l.style.opacity = '1';
            l.style.transform = 'translateY(0)';
        });
    }
}

/* ═══════════════════════════════════════════
   SCROLL PROGRESS BAR
   ═══════════════════════════════════════════ */
function initScrollProgress() {
    const bar = document.getElementById('scroll-progress');
    if (!bar) return;
    gsap.to(bar, {
        scaleX: 1, ease: 'none',
        scrollTrigger: {
            trigger: document.body,
            start: 'top top',
            end: 'bottom bottom',
            scrub: 0.5,  // Smoother scrub
        },
    });
}

/* ═══════════════════════════════════════════
   IMAGE REVEAL (clip-path wipe)
   ═══════════════════════════════════════════ */
function initImageReveal() {
    document.querySelectorAll('.image-reveal').forEach((el) => {
        ScrollTrigger.create({ trigger: el, start: 'top 80%', onEnter: () => el.classList.add('revealed'), once: true });
    });
}

/* ═══════════════════════════════════════════
   CARDS RISE ON SCROLL
   ═══════════════════════════════════════════ */
function initRiseCards() {
    gsap.utils.toArray('.rise-card').forEach((card, i) => {
        gsap.to(card, {
            y: 0, opacity: 1, duration: 1, delay: i * 0.12, ease: 'power3.out',
            scrollTrigger: { trigger: card, start: 'top 90%', toggleActions: 'play none none none' },
        });
    });
}

/* ═══════════════════════════════════════════
   STAT COUNTERS
   ═══════════════════════════════════════════ */
function initStatCounters() {
    document.querySelectorAll('.stat-item').forEach((item, i) => {
        gsap.to(item, {
            y: 0, opacity: 1, duration: 0.8, delay: i * 0.15, ease: 'power3.out',
            scrollTrigger: { trigger: item, start: 'top 85%', onEnter: () => animateCounter(item), once: true },
        });
    });
}

function animateCounter(item) {
    const valueEl = item.querySelector('.stat-value');
    if (!valueEl) return;
    const target = parseInt(valueEl.dataset.target);
    const obj = { value: 0 };
    gsap.to(obj, { value: target, duration: 2.5, ease: 'power2.out', onUpdate: () => { valueEl.textContent = Math.round(obj.value).toLocaleString(); } });
}

/* ═══════════════════════════════════════════
   INFINITE DRAG CAROUSEL
   ═══════════════════════════════════════════ */
function initInfiniteDrag() {
    const track = document.getElementById('drag-track');
    const wrapper = document.getElementById('drag-wrapper');
    if (!track || !wrapper) return;

    // Animate cards in
    gsap.utils.toArray('.drag-card').forEach((card, i) => {
        gsap.to(card, {
            y: 0, opacity: 1, duration: 0.8, delay: i * 0.08, ease: 'power3.out',
            scrollTrigger: { trigger: card, start: 'top 95%', once: true },
        });
    });

    // Auto-scroll + drag
    let pos = 0;
    let speed = 0.5;
    let isDragging = false;
    let startX, scrollStart;

    function autoScroll() {
        if (!isDragging) {
            pos -= speed;
            const halfWidth = track.scrollWidth / 2;
            if (Math.abs(pos) >= halfWidth) pos = 0;
            track.style.transform = `translateX(${pos}px)`;
        }
        requestAnimationFrame(autoScroll);
    }
    autoScroll();

    // Mouse drag
    wrapper.addEventListener('mousedown', (e) => {
        isDragging = true;
        startX = e.pageX;
        scrollStart = pos;
    });
    window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        pos = scrollStart + (e.pageX - startX);
    });
    window.addEventListener('mouseup', () => { isDragging = false; });

    // Touch drag
    wrapper.addEventListener('touchstart', (e) => {
        isDragging = true;
        startX = e.touches[0].pageX;
        scrollStart = pos;
    });
    wrapper.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        pos = scrollStart + (e.touches[0].pageX - startX);
    });
    wrapper.addEventListener('touchend', () => { isDragging = false; });

    // Hover effects
    document.querySelectorAll('.drag-card').forEach((card) => {
        card.addEventListener('mouseenter', () => { gsap.to(card, { scale: 1.03, rotation: 0, duration: 0.3 }); });
        card.addEventListener('mouseleave', () => {
            const orig = card.classList.contains('rotate-[-2deg]') ? -2 : 2;
            gsap.to(card, { scale: 1, rotation: orig, duration: 0.3 });
        });
    });
}

/* ═══════════════════════════════════════════
   TESTIMONIAL CAROUSEL
   ═══════════════════════════════════════════ */
function initTestimonialCarousel() {
    const slides = document.querySelectorAll('.testimonial-slide');
    const dots = document.querySelectorAll('.testimonial-dot');
    if (slides.length === 0) return;
    let current = 0, interval;

    function goTo(index) {
        slides.forEach((s, i) => { s.style.opacity = i === index ? '1' : '0'; s.style.transform = i === index ? 'translateY(0)' : 'translateY(20px)'; });
        dots.forEach((d, i) => { d.classList.toggle('bg-gold', i === index); d.classList.toggle('w-6', i === index); d.classList.toggle('bg-sand', i !== index); d.classList.toggle('w-2', i !== index); });
        current = index;
    }

    dots.forEach((dot) => { dot.addEventListener('click', () => { clearInterval(interval); goTo(parseInt(dot.dataset.index)); interval = setInterval(() => goTo((current + 1) % slides.length), 6000); }); });
    interval = setInterval(() => goTo((current + 1) % slides.length), 6000);
}

/* ═══════════════════════════════════════════
   IMAGE ZOOM ON SCROLL
   ═══════════════════════════════════════════ */
function initZoomScroll() {
    document.querySelectorAll('.zoom-scroll').forEach((el) => {
        gsap.fromTo(el, { scale: 1 }, { scale: 1.25, ease: 'none', scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true } });
    });
}

/* ═══════════════════════════════════════════
   SCROLL REVEAL
   ═══════════════════════════════════════════ */
function initScrollReveal() {
    document.querySelectorAll('.scroll-reveal').forEach((el) => {
        gsap.fromTo(el, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 85%', once: true } });
    });
}

/* ═══════════════════════════════════════════
   MAP ANIMATION — Draw route + reveal points
   ═══════════════════════════════════════════ */
function initMapAnimation() {
    const routePath = document.getElementById('route-path');
    const mapPoints = document.querySelectorAll('.map-point');
    const planeIcon = document.getElementById('plane-icon');
    if (!routePath) return;

    // Animate route drawing on scroll
    gsap.to(routePath, {
        strokeDashoffset: 0,
        duration: 3,
        ease: 'power2.inOut',
        scrollTrigger: { trigger: routePath, start: 'top 75%', once: true },
    });

    // Reveal map points with stagger
    mapPoints.forEach((point, i) => {
        gsap.to(point, {
            opacity: 1,
            duration: 0.6,
            delay: 1 + i * 0.3,
            ease: 'power2.out',
            scrollTrigger: { trigger: point, start: 'top 80%', once: true },
            onStart: () => point.classList.add('revealed'),
        });
    });

    // Show plane after route draws
    if (planeIcon) {
        gsap.to(planeIcon, {
            opacity: 1,
            duration: 0.5,
            delay: 3,
            scrollTrigger: { trigger: routePath, start: 'top 75%', once: true },
        });
    }
}

/* ═══════════════════════════════════════════
   BIG TEXT PARALLAX
   ═══════════════════════════════════════════ */
function initBigTextParallax() {
    const bigText = document.querySelector('.voyage-big-text');
    if (!bigText) return;

    gsap.fromTo(bigText,
        { x: '-5%' },
        {
            x: '5%',
            ease: 'none',
            scrollTrigger: { trigger: bigText, start: 'top bottom', end: 'bottom top', scrub: 1 },
        }
    );
}
