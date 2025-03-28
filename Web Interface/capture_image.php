<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);
header('Content-Type: application/json');

// Database connection parameters (update with your details)
$host = 'localhost';
$dbname = 'darts';
$user = 'dart_thrower';
$password = 'darts';

$data = json_decode(file_get_contents('php://input'), true);

// Validate input
if (empty($data['image']) || empty($data['player']) || empty($data['game_id'])) {
    echo json_encode(['status' => 'error', 'message' => 'Invalid input.']);
    exit;
}

// Database connection
try {
    $pdo = new PDO("pgsql:host=$host;dbname=$dbname", $user, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo json_encode(['status' => 'error', 'message' => 'Database connection failed: ' . $e->getMessage()]);
    exit;
}

// Assuming you want to save the image as a Base64 string in the database
$imageData = $data['image'];
$player = $data['player'];
$gameId = $data['game_id'];

// Remove the "data:image/png;base64," part if it exists
$imageData = preg_replace('/^data:image\/\w+;base64,/', '', $imageData);
$imageData = str_replace(' ', '+', $imageData); // Fix the base64 encoding issues

// Prepare the SQL to insert into the images table
$sql = "INSERT INTO images (game_id, player_name, image_data) VALUES (:game_id, :player_name, :image_data)";
$stmt = $pdo->prepare($sql);
$stmt->bindParam(':game_id', $gameId);
$stmt->bindParam(':player_name', $player);
$stmt->bindParam(':image_data', $imageData);

// Execute the query
if ($stmt->execute()) {
    echo json_encode(['status' => 'success', 'message' => 'Image uploaded and saved successfully to the database!']);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Failed to save image details to the database.']);
}
?>