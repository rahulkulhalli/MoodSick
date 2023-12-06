<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4 mt-5">
        <div class="card shadow">
          <div class="card-body">
            <h3 class="text-center mb-4">Login</h3>
            <form @submit.prevent="login">
              <div class="mb-3">
                <label for="email" class="form-label">Email address</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="credentials.email"
                  placeholder="Enter email"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="password" class="form-label">Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="credentials.password"
                  placeholder="Password"
                  required
                />
              </div>
              <button type="submit" class="btn btn-primary w-100">Login</button>
            </form>
            <div class="text-center mt-3">
              <p>
                Don't have an account?
                <nuxt-link to="/register">Register here</nuxt-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
  
  <script>
//   import axios from 'axios';

export default {
  data() {
    return {
      credentials: {
        email: "",
        password: "",
      },
    };
  },
  methods: {
    async login() {
      try {
        const response = await fetch("http://10.9.0.6/user/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(this.credentials),
        });

        if (!response.ok) {
          alert("Please try again.");
          throw new Error("Failed to Login");
        }
        const responseData = await response.json();
        if (responseData.message == "Login Successful") {
          sessionStorage.setItem("user_data", JSON.stringify(responseData.user_data))
          this.$router.push('/UserDashboard')
        } else if (responseData.message == "Invalid Credentials") {
          alert("Some Error Occurred! Pleaser Try Again!");
        } else {
          alert("Some Error Occurred! Pleaser Try Again!");
        }
      } catch (error) {
        alert("Some Error Occurred! Pleaser Try Again!");
      }
    },
  },
};
</script>
  