<template></template>

<script>
export default {
  data() {
    return {
      user_data: null,
      user_id: null,
    };
  },
  mounted() {
    this.user_data = JSON.parse(sessionStorage.getItem("user_data"));
    this.user_id = this.user_data.user_id;
    this.getGraphsData()
  },
  methods: {
    async getGraphsData() {
      try {
        const response = await fetch(
          "http://10.9.0.6/user/viz",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              user_id: this.user_id
            }),
          }
        );
        const responseData = await response.json();
        console.log(responseData);
        // if (responseData.message == "User Authorization Successful") {
        //   let user_data = JSON.parse(sessionStorage.getItem("user_data"));
        //   user_data["spotify_logged_in"] = true;
        //   sessionStorage.setItem("user_data", JSON.stringify(user_data));
        //   this.$router.push("/");
        // }
      } catch (error) {
        console.log(error);
        alert("Some Error Occurred! Pleaser Try Again!");
      }
    },
  },
};
</script>

<style>
</style>