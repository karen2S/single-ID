<?php
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Check if married
    $status = $_POST['maritalStatus'] ?? 'single';
    if ($status === 'married') {
        // Save data to session
        $_SESSION['fullName']      = $_POST['fullName']      ?? 'nan';
        $_SESSION['motherName']    = $_POST['motherName']    ?? 'nan';
        $_SESSION['sex']           = $_POST['sex']           ?? 'nan';
        $_SESSION['dob']           = $_POST['dob']           ?? 'nan';
        $_SESSION['placeOfBirth']  = $_POST['placeOfBirth']  ?? 'nan';
        $_SESSION['branchCode']    = $_POST['branchCode']    ?? 'nan';
        $_SESSION['npwp']          = $_POST['npwp']          ?? 'nan';
        $_SESSION['date_valid']    = $_POST['date_valid']    ?? 'nan';
        $_SESSION['nik']           = $_POST['nik']           ?? 'nan';
        $_SESSION['address']       = $_POST['address']       ?? 'nan';

        // Redirect to partner-data.html
        header("Location: partner-data.php");
        exit;
    }
}

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

// Get form data
$no_aggr = str_pad(mt_rand(1, 9), 1, '0', STR_PAD_LEFT); // start with non-zero

for ($i = 1; $i < 17; $i++) {
    $no_aggr .= mt_rand(0, 9);
}

$name_golive      = $_POST['fullName']      ?? $_SESSION['fullName']      ?? 'nan';
$nama_ibu_kandung = $_POST['motherName']    ?? $_SESSION['motherName']    ?? 'nan';
$sex              = $_POST['sex']           ?? $_SESSION['sex']           ?? 'nan';
$tgl_lahir        = $_POST['dob']           ?? $_SESSION['dob']           ?? 'nan';
$tempat_lahir     = $_POST['placeOfBirth']  ?? $_SESSION['placeOfBirth']  ?? 'nan';
$cd_sp            = $_POST['branchCode']    ?? $_SESSION['branchCode']    ?? 'nan';
$no_npwp          = $_POST['npwp']          ?? $_SESSION['npwp']          ?? 'nan';
$no_ktp_kitas     = $_POST['nik']           ?? $_SESSION['nik']           ?? 'nan';
$almt_rumah       = $_POST['address']       ?? $_SESSION['address']       ?? 'nan';
$dt_golive_valid  = $_POST['date_valid']    ?? $_SESSION['date_valid']    ?? 'nan';
$flag_pc          = "P";

$no_ktp_coborr = isset($_POST['nikCoBorrower']) ? $_POST['nikCoBorrower'] : "nan";
$name_coborr = isset($_POST['fullNameCoBorrower']) ? $_POST['fullNameCoBorrower'] : "nan";
$tgl_lahir_coborr = isset($_POST['dobCoBorrower']) ? $_POST['dobCoBorrower'] : "nan";
$alamat_coborr = isset($_POST['addressCoBorrower']) ? $_POST['addressCoBorrower'] : "nan";

$no_aggr_u          = strtoupper($no_aggr);
$name_golive_u      = strtoupper($name_golive);
$flag_pc_u          = strtoupper($flag_pc);
$nama_ibu_kandung_u = strtoupper($nama_ibu_kandung);
$sex_u              = strtoupper($sex);
$tgl_lahir_u        = strtoupper($tgl_lahir);
$tempat_lahir_u     = strtoupper($tempat_lahir);
$dt_golive_valid_u  = strtoupper($dt_golive_valid);
$cd_sp_u            = strtoupper($cd_sp);
$no_npwp_u          = strtoupper($no_npwp);
$no_ktp_kitas_u     = strtoupper($no_ktp_kitas);
$almt_rumah_u       = strtoupper($almt_rumah);
$no_ktp_coborr_u    = strtoupper($no_ktp_coborr);
$name_coborr_u      = strtoupper($name_coborr);
$tgl_lahir_coborr_u = strtoupper($tgl_lahir_coborr);
$alamat_coborr_u    = strtoupper($alamat_coborr);

// Start Cleansing
$python = "D:/App/Conda/python.exe";
$args = [
    escapeshellarg($name_golive_u),
    escapeshellarg($nama_ibu_kandung_u),
    escapeshellarg($tempat_lahir_u),
    escapeshellarg($no_npwp_u),
    escapeshellarg($no_ktp_kitas_u),
    escapeshellarg($almt_rumah_u),
    escapeshellarg($no_ktp_coborr_u),
    escapeshellarg($name_coborr_u),
    escapeshellarg($alamat_coborr_u)
];

$command = "$python cleanse.py " . implode(' ', $args) . " 2>&1";
$output = shell_exec($command);
$result = json_decode($output, true);

if ($result && isset($result[0])) {
    $cleansed = $result[0];
    $bigrams = $cleansed['bigrams'];
}

// Insert into bigram_index
foreach ($bigrams as $bg) {
    $name = $cleansed['cleaned_name'];
    $stmt_bigram = $conn->prepare("
    INSERT INTO bigram_index (bigram, group_values)
    VALUES (?, JSON_ARRAY(?))
    ON DUPLICATE KEY UPDATE 
        group_values = IF(
            JSON_CONTAINS(group_values, JSON_QUOTE(?)),
            group_values,
            JSON_ARRAY_APPEND(group_values, '$', ?)
        )");
    $stmt_bigram->bind_param("ssss", $bg, $name, $name, $name);
    $stmt_bigram->execute();
    $stmt_bigram->close(); // Close after each insert
}

// Make Single ID (SID)
$args = [
    escapeshellarg($cleansed['cleaned_name']),
    escapeshellarg($cleansed['cleaned_TEMPAT_LAHIR']),
    escapeshellarg($tgl_lahir_u),
    escapeshellarg($cleansed['cleaned_no_ktp']),
    escapeshellarg($cleansed['cleaned_no_npwp']),
    escapeshellarg($cleansed['cleaned_alamat']),
    escapeshellarg($cleansed['cleaned_NAMA_IBU_KANDUNG']),
    escapeshellarg($cd_sp_u),
    escapeshellarg($cleansed['cleaned_name_cob']),
    escapeshellarg($cleansed['cleaned_no_ktp_cob']),
    escapeshellarg($tgl_lahir_coborr_u),
    escapeshellarg($cleansed['cleaned_alamat_cob']),
];
$command = "$python sid.py " . implode(' ', $args) . " 2>&1";
$output = shell_exec($command);
echo "<pre>$output</pre>";
$result = json_decode($output, true);
if ($result && isset($result[0])) {
    $result_json = $result[0];
    $sid_value = $result_json['sid_value'];
    $sid_cobor_value = $result_json['sid_cobor_value'];
    $gid_value = $result_json['gid_value'];
    $match_found = $result_json['match_found'];
}
// var_dump($cleansed);
// var_dump($result_json);

// Prepare SQL insert
if ($match_found) {
    $sql = "INSERT INTO credit_cust (NO_AGGR, NAME_GOLIVE, flag_PC, NAMA_IBU_KANDUNG, SEX, TGL_LAHIR, TEMPAT_LAHIR, 
    DT_GOLIVE_VALID, CD_SP, NO_NPWP, NO_KTP_KITAS, ALMT_RUMAH, NO_KTP_COBORR, NAME_COBORR, TGL_LAHIR_COBORR, ALAMAT_COBORR,cleaned_NAMA_IBU_KANDUNG, 
    cleaned_TEMPAT_LAHIR, cleaned_name, cleaned_no_ktp, cleaned_no_npwp, cleaned_alamat, cleaned_name_cob, cleaned_no_ktp_cob, cleaned_alamat_cob, SID, SID_COBORR) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    $stmt_credit = $conn->prepare($sql);

    $stmt_credit->bind_param(
        "sssssssssssssssssssssssssss",
        $no_aggr_u,
        $name_golive_u,
        $flag_pc_u,
        $nama_ibu_kandung_u,
        $sex_u,
        $tgl_lahir_u,
        $tempat_lahir_u,
        $dt_golive_valid_u,
        $cd_sp_u,
        $no_npwp_u,
        $no_ktp_kitas_u,
        $almt_rumah_u,
        $no_ktp_coborr_u,
        $name_coborr_u,
        $tgl_lahir_coborr_u,
        $alamat_coborr_u,
        $cleansed['cleaned_NAMA_IBU_KANDUNG'],
        $cleansed['cleaned_TEMPAT_LAHIR'],
        $cleansed['cleaned_name'],
        $cleansed['cleaned_no_ktp'],
        $cleansed['cleaned_no_npwp'],
        $cleansed['cleaned_alamat'],
        $cleansed['cleaned_name_cob'],
        $cleansed['cleaned_no_ktp_cob'],
        $cleansed['cleaned_alamat_cob'],
        $sid_value,
        $sid_cobor_value
    );
    $stmt_credit->execute();
    $stmt_credit->close();

    // insert to monre_dict
    $result = $conn->query("SELECT MAX(id) AS latest_index FROM credit_cust");
    $row = $result->fetch_assoc();
    $latest_index = $row['latest_index'];

    $stmt_monre_dict = $conn->prepare("
        INSERT INTO monre_dict (cleaned_name, place_index)
        VALUES (?, JSON_ARRAY(?))
        ON DUPLICATE KEY UPDATE
            place_index = IF(
                JSON_CONTAINS(place_index, JSON_QUOTE(?)),
                place_index,
                JSON_ARRAY_APPEND(place_index, '$', ?)
            )");

    $stmt_monre_dict->bind_param("ssss", $name, $latest_index, $latest_index, $latest_index);
    $stmt_monre_dict->execute();
    $stmt_monre_dict->close();
} else {
    $sql = "INSERT INTO candidate_sid (NO_AGGR, NAME_GOLIVE, flag_PC, NAMA_IBU_KANDUNG, SEX, TGL_LAHIR, TEMPAT_LAHIR, 
    DT_GOLIVE_VALID, CD_SP, NO_NPWP, NO_KTP_KITAS, ALMT_RUMAH, NO_KTP_COBORR, NAME_COBORR, TGL_LAHIR_COBORR, ALAMAT_COBORR,cleaned_NAMA_IBU_KANDUNG, 
    cleaned_TEMPAT_LAHIR, cleaned_name, cleaned_no_ktp, cleaned_no_npwp, cleaned_alamat, cleaned_name_cob, cleaned_no_ktp_cob, cleaned_alamat_cob, SID, SID_COBORR) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    $stmt_credit = $conn->prepare($sql);

    $stmt_credit->bind_param(
        "sssssssssssssssssssssssssss",
        $no_aggr_u,
        $name_golive_u,
        $flag_pc_u,
        $nama_ibu_kandung_u,
        $sex_u,
        $tgl_lahir_u,
        $tempat_lahir_u,
        $dt_golive_valid_u,
        $cd_sp_u,
        $no_npwp_u,
        $no_ktp_kitas_u,
        $almt_rumah_u,
        $no_ktp_coborr_u,
        $name_coborr_u,
        $tgl_lahir_coborr_u,
        $alamat_coborr_u,
        $cleansed['cleaned_NAMA_IBU_KANDUNG'],
        $cleansed['cleaned_TEMPAT_LAHIR'],
        $cleansed['cleaned_name'],
        $cleansed['cleaned_no_ktp'],
        $cleansed['cleaned_no_npwp'],
        $cleansed['cleaned_alamat'],
        $cleansed['cleaned_name_cob'],
        $cleansed['cleaned_no_ktp_cob'],
        $cleansed['cleaned_alamat_cob'],
        $sid_value,
        $sid_cobor_value
    );
    $stmt_credit->execute();
    $stmt_credit->close();
}
$sql_get_credit_cust = "SELECT * FROM credit_cust WHERE SID = '$sid_value'";
$result = $conn->query($sql_get_credit_cust);

$stmt = $conn->prepare("
    SELECT * FROM credit_cust 
    WHERE SID IN (
        SELECT SID_BORR 
        FROM mst_sid_borr_coborr 
        WHERE GID = ?
    )
");
$stmt->bind_param("s", $gid_value);
$stmt->execute();
$result_group = $stmt->get_result();

$conn->close();
?>

<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SID Demo</title>
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
                <h2 class="">Aplikasi Kredit telah Dicatat!</h2>
                <?php if (isset($sid_value)): ?>
                    <p>SID : <strong><?= $sid_value ?></strong></p>
                <?php endif; ?>
                <?php if (isset($sid_cobor_value)): ?>
                    <p>SID COBORR : <strong><?= $sid_cobor_value ?></strong></p>
                <?php endif; ?>
                <?php if (isset($gid_value)): ?>
                    <p>GID : <strong><?= $gid_value ?></strong></p>
                <?php endif; ?>
                <div class="center-content">
                    <button onclick="window.location.href='index.html'" class="formbold-btn">
                        Back to Form</button>
                </div>
            </div>
        </div>
    </div>
    <!-- PERSONAL CREDIT HISTORY -->
    <div style="padding: 25px;">
        <h2 style="font-weight: 600; font-size: 28px; line-height: 34px; color: #07074d;">Aplikasi Kredit PERSONAL</h2>
        <table class="table table-striped table-hover" style="table-layout: fixed; width: 100%;">
            <colgroup>
                <col style="width: 150px;"> <!-- No Aggr -->
                <col style="width: 200px;"> <!-- Nama Lengkap -->
                <col style="width: 60px;"> <!-- Sex -->
                <col style="width: 120px;"> <!-- Tempat Lahir -->
                <col style="width: 120px;"> <!-- Tanggal Lahir -->
                <col style="width: 80px;"> <!-- CD SP -->
                <col style="width: 150px;"> <!-- NO KTP -->
                <col style="width: 150px;"> <!-- NO NPWP -->
                <col style="width: 200px;"> <!-- Alamat Rumah -->
                <col style="width: 100px;"> <!-- SID -->
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
                </tr>
            </thead>
            <tbody>
                <?php if ($result && $result->num_rows > 0): ?>
                    <?php while ($row = $result->fetch_assoc()): ?>
                        <tr>
                            <td><?= htmlspecialchars($row['NO_AGGR']) ?></td>
                            <td><?= htmlspecialchars($row['cleaned_name']) ?></td>
                            <td><?= htmlspecialchars($row['SEX']) ?></td>
                            <td><?= htmlspecialchars($row['cleaned_TEMPAT_LAHIR']) ?></td>
                            <td><?= htmlspecialchars($row['TGL_LAHIR']) ?></td>
                            <td><?= htmlspecialchars($row['CD_SP']) ?></td>
                            <td><?= htmlspecialchars($row['cleaned_no_ktp']) ?></td>
                            <td><?= htmlspecialchars($row['cleaned_no_npwp']) ?></td>
                            <td><?= htmlspecialchars($row['cleaned_alamat']) ?></td>
                            <td><?= htmlspecialchars($row['SID']) ?></td>
                        </tr>
                    <?php endwhile; ?>

                    <?php if (! $match_found): ?>
                        <tr>
                            <td><?= htmlspecialchars($no_aggr_u) ?></td>
                            <td><?= htmlspecialchars($cleansed['cleaned_name']) ?></td>
                            <td><?= htmlspecialchars($sex_u) ?></td>
                            <td><?= htmlspecialchars($cleansed['cleaned_TEMPAT_LAHIR']) ?></td>
                            <td><?= htmlspecialchars($tgl_lahir_u) ?></td>
                            <td><?= htmlspecialchars($cd_sp_u) ?></td>
                            <td><?= htmlspecialchars($cleansed['cleaned_no_ktp']) ?></td>
                            <td><?= htmlspecialchars($cleansed['cleaned_no_npwp']) ?></td>
                            <td><?= htmlspecialchars($cleansed['cleaned_alamat']) ?></td>
                            <td><strong style="color: orange;"><?= htmlspecialchars($sid_value) ?></strong></td>
                        </tr>
                    <?php endif; ?>

                <?php else: ?>
                    <tr>
                        <td colspan="10" style="text-align: center;">Data tidak ditemukan untuk SID <?= htmlspecialchars($sid_value) ?></td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
    <!-- GROUP CREDIT HISTORY -->
    <div style="padding: 25px;">
        <h2 style="font-weight: 600; font-size: 28px; line-height: 34px; color: #07074d;">Aplikasi Kredit GROUP</h2>
        <table class="table table-striped table-hover" style=" table-layout: fixed; width: 100%;">
            <colgroup>
                <col style="width: 150px;"> <!-- No Aggr -->
                <col style="width: 200px;"> <!-- Nama Lengkap -->
                <col style="width: 60px;"> <!-- Sex -->
                <col style="width: 120px;"> <!-- Tempat Lahir -->
                <col style="width: 120px;"> <!-- Tanggal Lahir -->
                <col style="width: 80px;"> <!-- CD SP -->
                <col style="width: 150px;"> <!-- NO KTP -->
                <col style="width: 150px;"> <!-- NO NPWP -->
                <col style="width: 200px;"> <!-- Alamat Rumah -->
                <col style="width: 100px;"> <!-- SID -->
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
                </tr>
            </thead>
            <tbody>
                <?php if ($result && $result_group->num_rows > 0): ?>
                    <?php while ($row = $result_group->fetch_assoc()): ?>
                        <tr>
                            <td><?= htmlspecialchars($row['NO_AGGR']) ?></td>
                            <td><?= htmlspecialchars($row['cleaned_name']) ?></td>
                            <td><?= htmlspecialchars($row['SEX']) ?></td>
                            <td><?= htmlspecialchars($row['cleaned_TEMPAT_LAHIR']) ?></td>
                            <td><?= htmlspecialchars($row['TGL_LAHIR']) ?></td>
                            <td><?= htmlspecialchars($row['CD_SP']) ?></td>
                            <td><?= htmlspecialchars($row['cleaned_no_ktp']) ?></td>
                            <td><?= htmlspecialchars($row['cleaned_no_npwp']) ?></td>
                            <td><?= htmlspecialchars($row['cleaned_alamat']) ?></td>
                            <td><?= htmlspecialchars($row['SID']) ?></td>
                        </tr>
                    <?php endwhile; ?>
                <?php else: ?>
                    <tr>
                        <td colspan="10" style="text-align: center;">Data tidak ditemukan untuk SID <?= htmlspecialchars($sid_value) ?></td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</body>

</html>