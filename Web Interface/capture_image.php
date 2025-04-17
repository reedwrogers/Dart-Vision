<?php
ob_start(); // Start output buffering
ini_set('display_errors', 1);
error_reporting(E_ALL);
header('Content-Type: application/json');

$host = 'localhost';
$dbname = 'darts';
$user = 'dart_thrower';
$password = 'darts';

$data = json_decode(file_get_contents('php://input'), true);

if (empty($data['image']) || empty($data['player']) || empty($data['game_id'])) {
    echo json_encode(['status' => 'error', 'message' => 'Invalid input.']);
    exit;
}

try {
    $pdo = new PDO("pgsql:host=$host;dbname=$dbname", $user, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo json_encode(['status' => 'error', 'message' => 'Database connection failed: ' . $e->getMessage()]);
    exit;
}

$imageData = $data['image'];
$player = $data['player'];
$gameId = $data['game_id'];

$imageData = preg_replace('/^data:image\/\w+;base64,/', '', $imageData);
$imageData = str_replace(' ', '+', $imageData);

// Save image temporarily (assuming your Python script knows to grab this)
$imagePath = 'uploads/temp_' . uniqid() . '.png';
file_put_contents($imagePath, base64_decode($imageData));

// Save to DB
$sql = "INSERT INTO images (game_id, player_name, image_data) VALUES (:game_id, :player_name, :image_data)";
$stmt = $pdo->prepare($sql);
$stmt->bindParam(':game_id', $gameId);
$stmt->bindParam(':player_name', $player);
$stmt->bindParam(':image_data', $imageData);

$response = ['status' => 'error', 'message' => 'Unknown error'];

if ($stmt->execute()) {
    // Now just call the Python script
    $output = shell_exec('bash -c "source /home/tars/jupyter/bin/activate && cd /home/tars/Projects/Dart-Vision/Web\ Interface && python3 utils.py 2>&1"');

    if ($output) {
        $response = [
            'status' => 'success',
            'message' => 'Image saved and processed.',
            'result' => trim($output)
        ];
    } else {
        $response = ['status' => 'error', 'message' => 'Python script failed to return output.'];
    }

    // Optional: unlink($imagePath); // Clean up if Python handles this
} else {
    $response = ['status' => 'error', 'message' => 'Failed to save image.'];
}

ob_end_clean(); // Clear any output

echo json_encode($response);

