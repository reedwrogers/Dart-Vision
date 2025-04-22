<?php
// get_scores.php
header('Content-Type: application/json');

// Replace with your actual DB credentials
$host = 'localhost';
$dbname = 'darts';
$user = 'dart_thrower';
$password = 'darts';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $user, $pass);
} catch (PDOException $e) {
    echo json_encode(['status' => 'error', 'message' => 'Database connection failed: ' . $e->getMessage()]);
    exit;
}

try {
    $stmt = $pdo->query("
        SELECT player, SUM(score) AS total_score
        FROM dart_throws
        WHERE game_mode = 'Cricket'
        GROUP BY player
        ORDER BY total_score DESC;
    ");

    $results = $stmt->fetchAll(PDO::FETCH_ASSOC);

    echo json_encode(['status' => 'success', 'data' => $results]);
} catch (PDOException $e) {
    echo json_encode(['status' => 'error', 'message' => $e->getMessage()]);
}
