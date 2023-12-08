<template>
    <div class="navbar-class">
  <div class="container">
    <div class="row">
      <div class="col-sm-12 d-flex my-2">
          <h5 class=" my-auto" style="color: whitesmoke;"> Welcome  <em> {{ user_name }} </em><span class="pl-3"> 🤓</span></h5>
        <img src="/moodsick_logo.png" alt="" style="margin-left: auto;max-height: 100%;max-width: 10vw;">
        <button
          class="btn btn-danger my-auto"
          style="margin-left: auto; max-height: fit-content;"
          @click="logoutAccount"
        >
          Logout
        </button>
      </div>
    </div>
    </div>
  </div>
  <!-- <nav class="navbar navbar-light bg-light">
  <div class="container-fluid">
    <a class="navbar-brand" href="#">
      <img src="/moodsick_logo.png" alt="" width="65" height="65" class="d-inline-block align-text-top">
        <h4 class="ml-2 mt-3 text-center d-inline-block" style="margin-left: auto;"> Welcome {{ user_name }} </h4>
        <button
          class="btn btn-danger"
          style="margin-left: auto"
          @click="logoutAccount"
        >
          Logout
        </button>
    </a>
  </div> -->
<!-- </nav> -->
</template>

<script>
export default {
  data() {
    return {
      user_name: null,
      user_data: null,
    };
  },
  mounted(){
    this.user_data = JSON.parse(sessionStorage.getItem("user_data"))
    this.user_name = this.user_data.name
  },
  methods: {
    logoutAccount() {
      sessionStorage.removeItem("user_data");
      this.$router.push("/Login");
    },
  },
};
</script>

<style scoped>
.navbar-class {
    background-image: linear-gradient(to right, #000000, #465362)

}
</style>