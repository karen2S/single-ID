<?php
session_start();

// Connect to MySQL
$host = "localhost";
$user = "root";
$pass = "";
$db   = "skripsi";

$conn = new mysqli($host, $user, $pass, $db);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$sql_get_credit_cust = "SELECT * FROM candidate_sid";
$result = $conn->query($sql_get_credit_cust);

// $conn->close();
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Page</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
</head>

<body>
    <div class="formbold-main-wrapper">
        <div class="formbold-result-wrapper">
            <div class="center-content">
                <img class="welcome-img" src="images/registered.jpg" alt="Vector Image">
            </div>
            <div class="formbold-form-title">
                <h2 style="text-align: center;">Candidate SID to Check</h2>
            </div>
        </div>
    </div>
    <div style="padding: 25px;">
        <!-- <h2 style="font-weight: 600; font-size: 28px; line-height: 34px; color: #07074d;">Aplikasi Kredit PERSONAL</h2> -->
        <table class="table" style="table-layout: fixed; width: 100%;white-space: normal !important;
        word-wrap: break-word;
        overflow-wrap: break-word;">
            <colgroup>
                <col style="width: 150px;"> <!-- No Aggr -->
                <col style="width: 150px;"> <!-- Nama Lengkap -->
                <col style="width: 50px;"> <!-- Sex -->
                <col style="width: 100px;"> <!-- Tempat Lahir -->
                <col style="width: 100px;"> <!-- Tanggal Lahir -->
                <col style="width: 80px;"> <!-- CD SP -->
                <col style="width: 130px;"> <!-- NO KTP -->
                <col style="width: 130px;"> <!-- NO NPWP -->
                <col style="width: 150px;"> <!-- Alamat Rumah -->
                <col style="width: 125px;"> <!-- SID -->
                <col style="width: 160px;"> <!-- Status -->
            </colgroup>
            <thead>
                <tr>
                    <th>No Aggr</th>
                    <th>Nama Lengkap</th>
                    <th>Sex</th>
                    <th>Tempat Lahir</th>
                    <th>Tanggal Lahir</th>
                    <th>CD SP</th>
                    <th>NO KTP</th>
                    <th>NO NPWP</th>
                    <th>Alamat Rumah</th>
                    <th>SID</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <?php if ($result && $result->num_rows > 0): ?>
                    <?php while ($row = $result->fetch_assoc()): ?>
                        <?php
                        $sid = $row['SID'];
                        $stmt_sid = $conn->prepare("SELECT * FROM credit_cust WHERE SID = ?");
                        $stmt_sid->bind_param("s", $sid);
                        $stmt_sid->execute();
                        $sid_result = $stmt_sid->get_result();
                        ?>

                        <?php while ($sid_row = $sid_result->fetch_assoc()): ?>
                            <tr style="background-color:#f0f0f0;">
                                <td><?= htmlspecialchars($sid_row['NO_AGGR']) ?></td>
                                <td><?= htmlspecialchars($sid_row['cleaned_name']) ?></td>
                                <td><?= htmlspecialchars($sid_row['SEX']) ?></td>
                                <td><?= htmlspecialchars($sid_row['cleaned_TEMPAT_LAHIR']) ?></td>
                                <td><?= htmlspecialchars($sid_row['TGL_LAHIR']) ?></td>
                                <td><?= htmlspecialchars($sid_row['CD_SP']) ?></td>
                                <td><?= htmlspecialchars($sid_row['cleaned_no_ktp']) ?></td>
                                <td><?= htmlspecialchars($sid_row['cleaned_no_npwp']) ?></td>
                                <td><?= htmlspecialchars($sid_row['cleaned_alamat']) ?></td>
                                <td><?= htmlspecialchars($sid_row['SID']) ?></strong></td>
                                <td></td>
                            </tr>
                        <?php endwhile; ?>
                        <?php $stmt_sid->close(); ?>

                        <tr style="background-color: #f5c45a; vertical-align: middle;">
                            <td style="vertical-align: middle;"><strong><?= htmlspecialchars($row['NO_AGGR']) ?></td>
                            <td style="vertical-align: middle;"><strong><?= htmlspecialchars($row['cleaned_name']) ?></td>
                            <td style="vertical-align: middle;"><strong><?= htmlspecialchars($row['SEX']) ?></td>
                            <td style="vertical-align: middle;"><strong><?= htmlspecialchars($row['cleaned_TEMPAT_LAHIR']) ?></td>
                            <td style="vertical-align: middle;"><strong><?= htmlspecialchars($row['TGL_LAHIR']) ?></td>
                            <td style="vertical-align: middle;"><strong><?= htmlspecialchars($row['CD_SP']) ?></td>
                            <td style="vertical-align: middle;"><strong><?= htmlspecialchars($row['cleaned_no_ktp']) ?></td>
                            <td style="vertical-align: middle;"><strong><?= htmlspecialchars($row['cleaned_no_npwp']) ?></td>
                            <td style="vertical-align: middle;"><strong><?= htmlspecialchars($row['cleaned_alamat']) ?></td>
                            <td style="vertical-align: middle;"><strong><?= htmlspecialchars($row['SID']) ?></strong></td>
                            <form action="approve_candidate.php" method="post">
                                <input type="hidden" name="no_aggr" value="<?= htmlspecialchars($row['NO_AGGR']) ?>">
                                <td>
                                    <button type="submit" name="action" value="approve" class="btn btn-success">Approve</button>
                                    <button type="submit" name="action" value="decline" class="btn btn-danger">Decline</button>
                                </td>
                            </form>
                        </tr>
                    <?php endwhile; ?>
                <?php else: ?>
                    <tr>
                        <td colspan="10" style="text-align: center;">No data found</td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</body>

</html>