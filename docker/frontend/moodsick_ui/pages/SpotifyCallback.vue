<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-12 text-center">
        <h1>Please wait... Redirecting you to Our Page ....</h1>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      spotify_code: null,
      user_id: null,
    };
  },
  mounted() {
    this.spotify_code = this.$route.query.code;
    this.user_id = this.$route.query.state;
    this.saveAuthCode();
  },
  methods: {
    async saveAuthCode() {
      try {
        const response = await fetch(
          "http://10.9.0.6/user/save-user-auth-code",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              user_id: this.user_id,
              code: this.spotify_code,
            }),
          }
        );
        if (!response.ok) {
          throw new Error("Failed to Login");
        }
        const responseData = await response.json();
        console.log(responseData);
        if (responseData.message == "User Authorization Successful") {
          let user_data = JSON.parse(sessionStorage.getItem("user_data"));
          user_data["spotify_logged_in"] = true;
          sessionStorage.setItem("user_data", JSON.stringify(user_data));
          this.$router.push("/");
        }
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