import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiService {
  static const Duration _timeout = Duration(seconds: 20);

  // Start FastAPI with:
  // python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  static String get baseUrl {
    if (kIsWeb) {
      return "http://127.0.0.1:8000";
    }

    // Use the PC's LAN IP when running on a real Android phone.
    // If using an Android emulator instead, change this to http://10.0.2.2:8000.
    if (defaultTargetPlatform == TargetPlatform.android) {
      return "http://192.168.1.3:8000";
    }

    return "http://127.0.0.1:8000";
  }

  /// Registers a new user via the backend (which saves to Google Sheets)
  static Future<Map<String, dynamic>> register(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse("$baseUrl/register"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "username": username.trim(),
          "password": password
        }),
      ).timeout(_timeout);

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {"success": true, "message": data["message"] ?? "Registration successful."};
      } else {
        return {"success": false, "message": data["detail"] ?? "Registration failed."};
      }
    } catch (e) {
      return {"success": false, "message": "Failed to connect to backend: $e"};
    }
  }

  /// Authenticates a user (verifying password matching in Google Sheets)
  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse("$baseUrl/login"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "username": username.trim(),
          "password": password
        }),
      ).timeout(_timeout);

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {"success": true, "message": "Login successful."};
      } else {
        return {"success": false, "message": data["detail"] ?? "Invalid credentials."};
      }
    } catch (e) {
      return {"success": false, "message": "Failed to connect to backend: $e"};
    }
  }

  /// Runs the web scraper + calculator pipeline for a stock symbol
  static Future<Map<String, dynamic>> analyzeStock(String symbol, double requiredReturn) async {
    try {
      final response = await http.post(
        Uri.parse("$baseUrl/analyze"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "symbol": symbol.trim().toUpperCase(),
          "required_return": requiredReturn
        }),
      ).timeout(_timeout);

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {"success": true, "data": data};
      } else {
        return {"success": false, "message": data["detail"] ?? "Analysis failed."};
      }
    } catch (e) {
      return {"success": false, "message": "Connection error: $e"};
    }
  }

  /// Fetches analysis history logged inside the Google Sheet
  static Future<List<dynamic>> fetchHistory() async {
    try {
      final response = await http.get(Uri.parse("$baseUrl/history")).timeout(_timeout);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data["status"] == "success") {
          return data["data"] ?? [];
        }
      }
      return [];
    } catch (e) {
      print("Failed to fetch history: $e");
      return [];
    }
  }
}