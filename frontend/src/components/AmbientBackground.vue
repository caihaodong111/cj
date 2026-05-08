<template>
  <div class="ambient-background" aria-hidden="true">
    <div class="nebula blue"></div>
    <div class="nebula gold"></div>
    <div class="breathing-line gold-1"></div>
    <div class="breathing-line gold-2"></div>
    <div class="scan-grid"></div>
    <div class="particles">
      <div
        v-for="i in 8"
        :key="i"
        class="particle"
        :style="{ animationDelay: `${i * 1.5}s` }"
      ></div>
    </div>
  </div>
</template>

<style scoped>
.ambient-background {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.nebula {
  position: absolute;
  width: 80vw;
  height: 70vh;
  filter: blur(120px);
  opacity: 0.28;
  mix-blend-mode: screen;
}

.nebula.blue {
  background: radial-gradient(circle, #0066ff, transparent 75%);
  top: -10%;
  left: -5%;
}

.nebula.gold {
  background: radial-gradient(circle, #ffaa00, transparent 75%);
  bottom: -10%;
  right: -5%;
}

.breathing-line {
  position: absolute;
  height: 1px;
  background: linear-gradient(90deg, transparent, #ffaa00, transparent);
  filter: blur(1px);
  opacity: 0.3;
  animation: breathe 8s infinite ease-in-out;
}

.gold-1 {
  width: 100%;
  top: 30%;
  left: -50%;
  transform: rotate(-5deg);
}

.gold-2 {
  width: 100%;
  right: -50%;
  bottom: 20%;
  transform: rotate(3deg);
  animation-delay: -4s;
}

@keyframes breathe {
  0%,
  100% {
    opacity: 0.1;
    transform: scaleX(0.8) translateY(0);
  }

  50% {
    opacity: 0.5;
    transform: scaleX(1.2) translateY(-20px);
  }
}

.scan-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: linear-gradient(to bottom, black, transparent);
  animation: gridMove 25s linear infinite;
}

@keyframes gridMove {
  from {
    background-position: 0 0;
  }

  to {
    background-position: 0 50px;
  }
}

.particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  bottom: -10px;
  width: 3px;
  height: 3px;
  background: #00ccff;
  border-radius: 50%;
  opacity: 0;
  animation: particleFloat 15s linear infinite;
}

@keyframes particleFloat {
  0% {
    opacity: 0;
    transform: translateY(0) translateX(0);
  }

  10% {
    opacity: 0.6;
  }

  90% {
    opacity: 0.4;
  }

  100% {
    opacity: 0;
    transform: translateY(-100vh) translateX(30px);
  }
}

.particle:nth-child(1) { left: 10%; }
.particle:nth-child(2) { left: 20%; }
.particle:nth-child(3) { left: 30%; }
.particle:nth-child(4) { left: 40%; }
.particle:nth-child(5) { left: 50%; }
.particle:nth-child(6) { left: 60%; }
.particle:nth-child(7) { left: 70%; }
.particle:nth-child(8) { left: 80%; }
</style>
