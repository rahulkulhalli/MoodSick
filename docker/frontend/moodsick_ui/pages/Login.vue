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
                  <input type="email" class="form-control" id="email" v-model="credentials.email" placeholder="Enter email" required>
                </div>
                <div class="mb-4">
                  <label for="password" class="form-label">Password</label>
                  <input type="password" class="form-control" id="password" v-model="credentials.password" placeholder="Password" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Login</button>
              </form>
              <div class="text-center mt-3">
    <p>Don't have an account? <nuxt-link to="/register">Register here</nuxt-link></p>
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
          email: '',
          password: ''
        }
      };
    },
    methods: {
      login() {
        try {
          this.$router.push('UserDashboard')

          // const response = await axios.post('YOUR_API_ENDPOINT', this.credentials);
          // Handle success, store the token, redirect, etc.
        } catch (error) {
          console.error(error);
          // Handle error
        }
      }
    }
  };
  </script>
  