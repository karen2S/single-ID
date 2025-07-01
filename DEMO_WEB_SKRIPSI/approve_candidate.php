<?php
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $action = $_POST['action']; // approve or decline
    $no_aggr = $_POST['no_aggr'];

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

    if ($action === "approve") {
        // 1. Fetch data from candidate_sid
        $query = "SELECT * FROM candidate_sid WHERE NO_AGGR = ?";
        $stmt_fetch = $conn->prepare($query);
        $stmt_fetch->bind_param("s", $no_aggr);
        $stmt_fetch->execute();
        $result = $stmt_fetch->get_result();

        if ($row = $result->fetch_assoc()) {
            // 2. Assign variables from the fetched row
            $no_aggr_u = $row['NO_AGGR'];
            $name_golive_u = $row['NAME_GOLIVE'];
            $flag_pc_u = $row['flag_PC'];
            $nama_ibu_kandung_u = $row['NAMA_IBU_KANDUNG'];
            $sex_u = $row['SEX'];
            $tgl_lahir_u = $row['TGL_LAHIR'];
            $tempat_lahir_u = $row['TEMPAT_LAHIR'];
            $dt_golive_valid_u = $row['DT_GOLIVE_VALID'];
            $cd_sp_u = $row['CD_SP'];
            $no_npwp_u = $row['NO_NPWP'];
            $no_ktp_kitas_u = $row['NO_KTP_KITAS'];
            $almt_rumah_u = $row['ALMT_RUMAH'];
            $no_ktp_coborr_u = $row['NO_KTP_COBORR'];
            $name_coborr_u = $row['NAME_COBORR'];
            $tgl_lahir_coborr_u = $row['TGL_LAHIR_COBORR'];
            $alamat_coborr_u = $row['ALAMAT_COBORR'];

            // Cleansed fields
            $cleansed = $row; // simplify reference
            $sid_value = $row['SID'];
            $sid_cobor_value = $row['SID_COBORR'];
            $name = $row['cleaned_name'];

            // 3. Insert into credit_cust
            $sql = "INSERT INTO credit_cust (
            NO_AGGR, NAME_GOLIVE, flag_PC, NAMA_IBU_KANDUNG, SEX, TGL_LAHIR, TEMPAT_LAHIR,
            DT_GOLIVE_VALID, CD_SP, NO_NPWP, NO_KTP_KITAS, ALMT_RUMAH, NO_KTP_COBORR, NAME_COBORR,
            TGL_LAHIR_COBORR, ALAMAT_COBORR, cleaned_NAMA_IBU_KANDUNG, cleaned_TEMPAT_LAHIR,
            cleaned_name, cleaned_no_ktp, cleaned_no_npwp, cleaned_alamat, cleaned_name_cob,
            cleaned_no_ktp_cob, cleaned_alamat_cob, SID, SID_COBORR
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

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

            // 4. Insert into monre_dict
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

            $stmt_delete = $conn->prepare("DELETE FROM candidate_sid WHERE NO_AGGR = ?");
            $stmt_delete->bind_param("s", $no_aggr);
            $stmt_delete->execute();
            $stmt_delete->close();

            if ($sid_cobor_value !== null) {
                $query = "SELECT 1 FROM mst_sid_borr_coborr WHERE SID_BORR = ? AND SID_COBORR = ?";
                $stmt = $conn->prepare($query);
                $stmt->bind_param("ss", $sid_value, $sid_cobor_value);
            } else {
                $query = "SELECT 1 FROM mst_sid_borr_coborr WHERE SID_BORR = ? AND SID_COBORR IS NULL";
                $stmt = $conn->prepare($query);
                $stmt->bind_param("s", $sid_value);
            }

            $stmt->execute();
            $result = $stmt->get_result();

            if ($result->num_rows === 0) {
                $python = "D:/App/Conda/python.exe";
                $args = [
                    escapeshellarg($sid_value),
                    escapeshellarg($sid_cobor_value)
                ];

                $command = "$python regroup_gid.py " . implode(' ', $args) . " 2>&1";
                $output = shell_exec($command);
            }
        }
        $stmt_fetch->close();
    } elseif ($action === "decline") {

        $query = "SELECT * FROM candidate_sid WHERE NO_AGGR = ?";
        $stmt_fetch = $conn->prepare($query);
        $stmt_fetch->bind_param("s", $no_aggr);
        $stmt_fetch->execute();
        $result = $stmt_fetch->get_result();

        if ($row = $result->fetch_assoc()) {
            $kode_cabang = $row['CD_SP'];
            $stmt_count = $conn->prepare("SELECT COUNT FROM sp_count WHERE CD_SP = ?");
            $stmt_count->bind_param("s", $kode_cabang);
            $stmt_count->execute();
            $count_result = $stmt_count->get_result();

            if ($count_row = $count_result->fetch_assoc()) {
                $current_count = (int)$count_row['COUNT'];
                $new_count = $current_count + 1;

                $sid_value = $kode_cabang . str_pad($new_count, 7, "0", STR_PAD_LEFT);

                $stmt_update = $conn->prepare("UPDATE sp_count SET COUNT = ? WHERE CD_SP = ?");
                $stmt_update->bind_param("is", $new_count, $kode_cabang);
                $stmt_update->execute();
                $stmt_update->close();
            }
            
            $stmt_count->close();

            $no_aggr_u = $row['NO_AGGR'];
            $name_golive_u = $row['NAME_GOLIVE'];
            $flag_pc_u = $row['flag_PC'];
            $nama_ibu_kandung_u = $row['NAMA_IBU_KANDUNG'];
            $sex_u = $row['SEX'];
            $tgl_lahir_u = $row['TGL_LAHIR'];
            $tempat_lahir_u = $row['TEMPAT_LAHIR'];
            $dt_golive_valid_u = $row['DT_GOLIVE_VALID'];
            $cd_sp_u = $row['CD_SP'];
            $no_npwp_u = $row['NO_NPWP'];
            $no_ktp_kitas_u = $row['NO_KTP_KITAS'];
            $almt_rumah_u = $row['ALMT_RUMAH'];
            $no_ktp_coborr_u = $row['NO_KTP_COBORR'];
            $name_coborr_u = $row['NAME_COBORR'];
            $tgl_lahir_coborr_u = $row['TGL_LAHIR_COBORR'];
            $alamat_coborr_u = $row['ALAMAT_COBORR'];

            $cleansed = $row; 
            $sid_cobor_value = $row['SID_COBORR'];
            $name = $row['cleaned_name'];

            $sql = "INSERT INTO credit_cust (
            NO_AGGR, NAME_GOLIVE, flag_PC, NAMA_IBU_KANDUNG, SEX, TGL_LAHIR, TEMPAT_LAHIR,
            DT_GOLIVE_VALID, CD_SP, NO_NPWP, NO_KTP_KITAS, ALMT_RUMAH, NO_KTP_COBORR, NAME_COBORR,
            TGL_LAHIR_COBORR, ALAMAT_COBORR, cleaned_NAMA_IBU_KANDUNG, cleaned_TEMPAT_LAHIR,
            cleaned_name, cleaned_no_ktp, cleaned_no_npwp, cleaned_alamat, cleaned_name_cob,
            cleaned_no_ktp_cob, cleaned_alamat_cob, SID, SID_COBORR
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

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

            $stmt_delete = $conn->prepare("DELETE FROM candidate_sid WHERE NO_AGGR = ?");
            $stmt_delete->bind_param("s", $no_aggr);
            $stmt_delete->execute();
            $stmt_delete->close();

            $python = "D:/App/Conda/python.exe";
            $args = [
                escapeshellarg($sid_value),
                escapeshellarg($sid_cobor_value)
            ];

            $command = "$python regroup_gid.py " . implode(' ', $args) . " 2>&1";
            $output = shell_exec($command);
        }

        $stmt_fetch->close();
    }

    $conn->close();

}

if ($action === 'approve') {
    // approve logic...
    $_SESSION['message'] = "NO_AGGR $no_aggr has been APPROVED.";
} elseif ($action === 'decline') {
    // decline logic...
    $_SESSION['message'] = "NO_AGGR $no_aggr has been DECLINED.";
}

header("Location: admin.php");
exit;
?>