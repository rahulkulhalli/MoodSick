<template>
  <div class="container">
    <div class="row mt-2">
      <div class="col-sm-12 d-flex">
        <h4> Welcome {{ user_name }} </h4>
        <button
          class="btn btn-danger"
          style="margin-left: auto"
          @click="logoutAccount"
        >
          Logout
        </button>
      </div>
    </div>
  </div>
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

<style>
</style>