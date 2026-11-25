import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:maat_presupuesto/app/router.dart';
import 'package:maat_presupuesto/core/tema/tema_maat.dart';
import 'package:maat_presupuesto/core/tema/tokens_maat.dart';

class AppMaatPresupuesto extends ConsumerWidget {
  const AppMaatPresupuesto({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'Maat Presupuesto',
      debugShowCheckedModeBanner: false,
      theme: temaMaat(TokensMaat.claro, Brightness.light),
      darkTheme: temaMaat(TokensMaat.oscuro, Brightness.dark),
      locale: const Locale('es'),
      supportedLocales: const [Locale('es')],
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      routerConfig: ref.watch(routerProvider),
    );
  }
}
