<template>
  <div class="splash-screen">
    <div class="spinner-wrapper">
      <h5 class="">{{ user_message }}</h5>
      <!-- <div class="spinner"></div> -->
      <img src="/moodsick_logo.png" alt="" class="spinner">
    </div>
  </div>
</template>
  
<script>
export default {
  props: {
    user_message: {
      type: String,
      default: null,
    },
  },
};
</script>

  <style scoped>
.splash-screen {
  /* background: #f2f0ee; */
  width: 100vw;
  height: 100vh;
  position: fixed;
  z-index: 50;
}

.spinner-wrapper {
  position: absolute;
  left: 50%;
  top: 50%;

  transform: translate(-60%, -65%);
}
.spinner {
  width: 80px;
  height: 80px;
  margin: 100px 270px;
  background-image: url(/moodsick_logo.png);

  border-radius: 100%;
  -webkit-animation: sk-scaleout 3s infinite ease-in-out;
  animation: sk-scaleout 3s infinite ease-in-out;
}


.message-user{
  -webkit-animation: sk-scaleout 1s infinite ease-in-out;
  animation: sk-scaleout 2s infinite ease-in-out;
}
@-webkit-keyframes sk-scaleout {
  0% {
    -webkit-transform: scale(0);
  }
  100% {
    -webkit-transform: scale(1);
    opacity: 0;
  }
}

@keyframes sk-scaleout {
  0% {
    -webkit-transform: scale(0);
    transform: scale(0);
  }
  100% {
    -webkit-transform: scale(1);
    transform: scale(1);
    opacity: 0;
  }
}
</style>