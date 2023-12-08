<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4 mt-5">
        <div class="card shadow">
          <div class="card-body">
            <h3 class="text-center mb-4">Register</h3>
            <form @submit.prevent="register">
              <div class="mb-3">
                <label for="email" class="form-label">Your Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="email"
                  v-model="user.name"
                  placeholder="Enter Name"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email address</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="user.email"
                  placeholder="Enter email"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="user.password"
                  placeholder="Password"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label"
                  >Confirm Password</label
                >
                <input
                  type="password"
                  class="form-control"
                  id="confirmPassword"
                  v-model="user.confirmPassword"
                  placeholder="Confirm Password"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="age" class="form-label">Age</label>
                <input
                  type="number"
                  class="form-control"
                  id="age"
                  v-model="user.age"
                  placeholder="Enter your age"
                  required
                />
              </div>

              <!-- <div class="mb-4">
                <label for="gender" class="form-label">Gender</label>
                <select
                  class="form-select"
                  id="gender"
                  v-model="user.gender"
                  required
                >
                  <option value="" disabled selected>Select your gender</option>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                  <option value="nonBinary">Non-Binary</option>
                  <option value="transgender">Transgender</option>
                  <option value="intersex">Intersex</option>
                  <option value="genderqueer">Genderqueer</option>
                  <option value="genderfluid">Genderfluid</option>
                  <option value="questioning">Questioning</option>
                  <option value="agender">Agender</option>
                  <option value="other">Other</option>
                </select>
              </div> -->
              <button type="submit" class="btn btn-primary w-100">
                Register
              </button>
            </form>
            <p>
              Already have an account?
              <nuxt-link to="/login">Login here</nuxt-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
  
  <script>
export default {
  data() {
    return {
      user: {
        email: "",
        password: "",
        confirmPassword: "",
        age: null, 
        gender: "",
        name: ""
      },
    };
  },
  methods: {
    async register() {
      try {
        const response = await fetch("http://10.9.0.6/user/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(this.user),
        });

        if (!response.ok) {
          throw new Error("Failed to register");
        }
        const responseData = await response.json();
        console.log("responseData", responseData);
        if (responseData.Status == true) {
          await this.$router.push("/Login")
        } else if (responseData.Status == "Already Exists") {
          alert("Email Already Exists");
        } else if (responseData.Status == false) {
          alert("Some Error Occurred! Pleaser Try Again!");
        } else {
          alert("Some Error Occurred! Pleaser Try Again!");
        }
      } catch (error) {
        console.error(error);
        alert("Some Error Occurred! Pleaser Try Again!");
      }
    },
  },
};
</script>
  