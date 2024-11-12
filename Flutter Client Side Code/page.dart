import 'package:flutter/material.dart';
import 'main.dart';

class DemoPage extends StatefulWidget {
  const DemoPage({super.key});

  @override
  State<DemoPage> createState() => _DemoPageState();
}

class _DemoPageState extends State<DemoPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("ISL"),),
      body: SafeArea(
        child: Container(
          child: ElevatedButton(onPressed: () {
            Navigator.push(context, MaterialPageRoute(builder: (context) => CameraScreen()));
          }, child: Text("Check")),
        ),
      ),
    );
  }
}
