import 'package:flutter/material.dart';
import 'package:{{feature_snake}}/{{feature_snake}}.dart';

class {{view_pascal}}App extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "{{view_pascal}}",
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: {{view_pascal}}(title: '{{view_pascal}} Home Page'),
    );
  }
}

class {{view_pascal}} extends StatefulWidget {
  final String title;

  const {{view_pascal}}({super.key, required this.title});

  @override
  State<{{view_pascal}}> createState() => {{view_pascal}}State();
}

class {{view_pascal}}State extends State<{{view_pascal}}> {
  int _counter = 0;
  final _calculator = Calculator();

  void _incrementCounter() {
    setState(() {
      _counter = _calculator.addOne(_counter);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'You have pushed the button this many times:',
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}
