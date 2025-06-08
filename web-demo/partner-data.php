<?php
session_start();
?>

<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SID Demo</title>
  <link rel="stylesheet" href="style.css">
</head>

<body>
  <div class="formbold-main-wrapper">
    <div class="formbold-form-wrapper">

      <img class="welcome-img" src="images/partner.png" alt="Vector Image">

      <form action="register.php" method="POST" id="customerForm">
        <div class="formbold-form-title">
          <h2 class="">Pengisian Data Co-Borrower</h2>
          <p>
            Please fill out the form with the customer's partner details.
          </p>
        </div>

        <div class="formbold-mb-3">
          <label for="fullNameCoBorrower" class="formbold-form-label">
            Nama Lengkap Co-Borrower
          </label>
          <input
            type="text"
            name="fullNameCoBorrower"
            id="fullNameCoBorrower"
            class="formbold-form-input"
            style="text-transform: uppercase;"
            required />
        </div>

        <div class="formbold-input-flex">
          <div>
            <label for="nikCoBorrower" class="formbold-form-label"> NIK / KITAS Co-Borrower </label>
            <input
              type="text"
              name="nikCoBorrower"
              id="nikCoBorrower"
              class="formbold-form-input"
              maxlength="16"
              minlength="11"
              pattern="\d{11,16}" />
          </div>

          <div>
            <label for="dobCoBorrower" class="formbold-form-label"> Tanggal Lahir Co-Borrower </label>
            <input
              type="date"
              name="dobCoBorrower"
              id="dobCoBorrower"
              class="formbold-form-input"
              required />
          </div>
        </div>

        <div class="formbold-mb-3">
          <label for="  " class="formbold-form-label">
            Alamat Rumah
          </label>
          <input
            type="text"
            name="addressCoBorrower"
            id="addressCoBorrower"
            class="formbold-form-input"
            style="text-transform: uppercase;"
            required />
        </div>
        <div class="center-content">
          <button onclick="window.location.href='index.html'" class="formbold-btn">
            << Back</button>
              <button type="submit" id="submitButton" class="formbold-btn">Register Now</button>
        </div>
      </form>
    </div>
  </div>
  <script src="script.js"></script>
</body>

</html>