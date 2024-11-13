// main.dart
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:isl/MainHomePage.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:typed_data';
import 'package:image/image.dart' as img;

List<CameraDescription> cameras = [];

// Future<void> main() async {
//   WidgetsFlutterBinding.ensureInitialized();
//   cameras = await availableCameras();
//   runApp(MyApp());
// }

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  cameras = await availableCameras();
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: MainHomePage(),
    );
  }
}


class CameraScreen extends StatefulWidget {
  @override
  _CameraScreenState createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  late CameraController _cameraController;
  late Socket _socket;
  bool _isStreaming = false;
  String _serverMessage = "";

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _connectToServer();
  }

  void _initializeCamera() async {
    try {
      _cameraController = CameraController(cameras[0], ResolutionPreset.medium);
      await _cameraController.initialize();
      setState(() {});
    } catch (e) {
      print("Failed to initialize camera: $e");
    }
  }

  void _connectToServer() async {
    try {
      _socket = await Socket.connect('192.168.31.133', 12343);
      print('Connected to server at 192.168.31.133:12343');
      _receiveMessagesFromServer();
    } catch (e) {
      print('Failed to connect to server: $e');
    }
  }

  void _receiveMessagesFromServer() {
    _socket.listen(
          (Uint8List data) {
        final serverResponse = String.fromCharCodes(data);
        print('Server: $serverResponse');
      },
      onError: (error) {
        print('Error receiving data from server: $error');
        _socket.destroy();
      },
      onDone: () {
        print('Server connection closed');
        _socket.destroy();
      },
    );
  }

  void _startStreaming() async {
    if (!_cameraController.value.isInitialized) {
      print('Error: Camera is not initialized');
      return;
    }

    _isStreaming = true;
    while (_isStreaming) {
      try {
        XFile image = await _cameraController.takePicture();
        Uint8List imageBytes = await image.readAsBytes();
        String base64Image = base64Encode(imageBytes);
        String message = base64Image + '<END_OF_IMAGE>';

        if (_socket != null) {
          _socket.write(message);
        }
        // Ensure ~24 FPS by using appropriate delay.
        // await Future.delayed(Duration(milliseconds: 42));
      } catch (e) {
        print('Failed to send image: $e');
        break;
      }
    }
  }

  void _stopStreaming() {
    setState(() {
      _isStreaming = false;
    });
  }

  @override
  void dispose() {
    _isStreaming = false;
    _cameraController?.dispose();
    _socket?.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_cameraController == null || !_cameraController.value.isInitialized) {
      return Scaffold(
        appBar: AppBar(title: Text('Camera Streamer')),
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text('Camera Streamer')),
      body: Column(
        children: [
          AspectRatio(
            aspectRatio: _cameraController.value.aspectRatio,
            child: CameraPreview(_cameraController),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton(
                onPressed: _isStreaming ? null : _startStreaming,
                child: Text('Start Streaming'),
              ),
              SizedBox(width: 10),
              ElevatedButton(
                onPressed: _isStreaming ? _stopStreaming : null,
                child: Text('Stop Streaming'),
              ),
              // SizedBox(height: 20),
              // Text(
              //   'Server Message: $_serverMessage',
              //   style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              // ),
            ],
          ),
        ],
      ),
    );
  }
}
