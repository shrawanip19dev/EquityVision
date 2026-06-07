import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import 'login_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final _searchController = TextEditingController();
  final _returnController = TextEditingController(text: "15.0");
  
  bool _isLoading = false;
  String? _errorMessage;
  Map<String, dynamic>? _analysisResult;
  List<dynamic> _history = [];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _returnController.dispose();
    super.dispose();
  }

  Future<void> _loadHistory() async {
    final history = await ApiService.fetchHistory();
    setState(() {
      _history = history;
    });
  }

  Future<void> _handleAnalyze() async {
    final symbol = _searchController.text.trim();
    final requiredReturnText = _returnController.text.trim();
    
    if (symbol.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Please enter a stock symbol"),
          backgroundColor: AppTheme.neonRed,
        ),
      );
      return;
    }

    double requiredReturn = 15.0;
    try {
      requiredReturn = double.parse(requiredReturnText);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Please enter a valid number for required return"),
          backgroundColor: AppTheme.neonRed,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _analysisResult = null;
    });

    final result = await ApiService.analyzeStock(symbol, requiredReturn);

    setState(() {
      _isLoading = false;
    });

    if (result["success"] == true) {
      setState(() {
        _analysisResult = result["data"];
      });
      _loadHistory(); // Reload history after successfully saving new results
    } else {
      setState(() {
        _errorMessage = result["message"];
      });
    }
  }

  void _logout() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text("EquityVision"),
        actions: [
          IconButton(
            onPressed: _logout,
            icon: const Icon(Icons.logout),
            tooltip: "Logout",
          ),
        ],
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isLargeScreen = constraints.maxWidth > 700;
          
          return SingleChildScrollView(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Welcome Text
                Text(
                  "Intrinsics Valuation Dashboard",
                  style: textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                const Text(
                  "Scrape screener metrics & discount them to calculate stock value.",
                  style: TextStyle(color: AppTheme.textSecondary),
                ),
                const SizedBox(height: 24),

                // Search Box Panel
                _buildSearchPanel(isLargeScreen),
                const SizedBox(height: 24),

                // Loading Spinner
                if (_isLoading) ...[
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 40.0),
                      child: CircularProgressIndicator(),
                    ),
                  ),
                ],

                // Error Banner
                if (_errorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppTheme.neonRed.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppTheme.neonRed.withOpacity(0.3)),
                    ),
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(color: AppTheme.neonRed, fontWeight: FontWeight.w600),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],

                // Results Card
                if (_analysisResult != null) ...[
                  _buildResultsCard(textTheme),
                  const SizedBox(height: 32),
                ],

                // History Title
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      "History Log (Google Sheets)",
                      style: textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    IconButton(
                      icon: const Icon(Icons.refresh, color: AppTheme.primaryBlue),
                      onPressed: _loadHistory,
                      tooltip: "Refresh history",
                    ),
                  ],
                ),
                const Divider(color: AppTheme.borderGrey, height: 16),
                const SizedBox(height: 8),

                // History List
                _buildHistoryList(),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildSearchPanel(bool isLargeScreen) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderGrey),
      ),
      child: isLargeScreen
          ? Row(
              children: [
                Expanded(
                  flex: 3,
                  child: TextFormField(
                    controller: _searchController,
                    decoration: const InputDecoration(
                      labelText: "Enter Stock Ticker (e.g. APARINDS)",
                      prefixIcon: Icon(Icons.search, color: AppTheme.textSecondary),
                    ),
                    textCapitalization: TextCapitalization.characters,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: TextFormField(
                    controller: _returnController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: "Required Return CAGR %",
                      prefixIcon: Icon(Icons.trending_up, color: AppTheme.textSecondary),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                SizedBox(
                  height: 52,
                  child: ElevatedButton.icon(
                    onPressed: _handleAnalyze,
                    icon: const Icon(Icons.auto_graph),
                    label: const Text("ANALYZE"),
                  ),
                ),
              ],
            )
          : Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextFormField(
                  controller: _searchController,
                  decoration: const InputDecoration(
                    labelText: "Enter Stock Ticker (e.g. APARINDS)",
                    prefixIcon: Icon(Icons.search, color: AppTheme.textSecondary),
                  ),
                  textCapitalization: TextCapitalization.characters,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _returnController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: "Required Return CAGR %",
                    prefixIcon: Icon(Icons.trending_up, color: AppTheme.textSecondary),
                  ),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: _handleAnalyze,
                  icon: const Icon(Icons.auto_graph),
                  label: const Text("ANALYZE STOCK"),
                ),
              ],
            ),
    );
  }

  Widget _buildResultsCard(TextTheme textTheme) {
    final res = _analysisResult!;
    final isUndervalued = res["status"] == "UNDERVALUED";
    final themeColor = isUndervalued ? AppTheme.neonGreen : AppTheme.neonRed;
    final upsidePct = res["upside_percent"] ?? 0.0;
    
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderGrey),
        boxShadow: [
          BoxShadow(
            color: themeColor.withOpacity(0.05),
            blurRadius: 20,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Card Header / Title
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            decoration: BoxDecoration(
              color: const Color(0xFF131620),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                topRight: Radius.circular(20),
              ),
              border: Border(bottom: BorderSide(color: AppTheme.borderGrey.withOpacity(0.5))),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        res["stock_name"] ?? res["symbol"],
                        style: textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        "Ticker: ${res["symbol"]}",
                        style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                  decoration: BoxDecoration(
                    color: themeColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: themeColor.withOpacity(0.4)),
                  ),
                  child: Text(
                    res["status"] ?? "",
                    style: TextStyle(
                      color: themeColor,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ],
            ),
          ),

          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                // Highlight Price vs Fair Value row
                Row(
                  children: [
                    Expanded(
                      child: _buildMetricTile(
                        "Current Price",
                        "₹${res["current_price"]}",
                        Icons.monetization_on_outlined,
                        AppTheme.textPrimary,
                      ),
                    ),
                    Container(width: 1, height: 50, color: AppTheme.borderGrey),
                    Expanded(
                      child: _buildMetricTile(
                        "Intrinsic Fair Value",
                        "₹${res["fair_value"]}",
                        Icons.star_border_purple500,
                        themeColor,
                      ),
                    ),
                  ],
                ),
                const Divider(color: AppTheme.borderGrey, height: 32),

                // Return details row
                Row(
                  children: [
                    Expanded(
                      child: _buildMetricTile(
                        "Upside / Downside",
                        "${upsidePct > 0 ? '+' : ''}$upsidePct%",
                        upsidePct > 0 ? Icons.trending_up : Icons.trending_down,
                        upsidePct > 0 ? AppTheme.neonGreen : AppTheme.neonRed,
                      ),
                    ),
                    Container(width: 1, height: 50, color: AppTheme.borderGrey),
                    Expanded(
                      child: _buildMetricTile(
                        "Margin of Safety",
                        "${res["margin_of_safety"]}%",
                        Icons.shield_outlined,
                        isUndervalued ? AppTheme.neonGreen : AppTheme.textSecondary,
                      ),
                    ),
                  ],
                ),
                const Divider(color: AppTheme.borderGrey, height: 32),

                // Financial Ratios Table
                const Text(
                  "Valuation Model Projections",
                  style: TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                _buildProjectionRow("Stock PE (Target Multiplier)", "${res["stock_pe"]}x"),
                _buildProjectionRow("Historical Stock Return (3Yr CAGR)", "${res["historical_return_3yr"]}%"),
                _buildProjectionRow("Earnings Growth Rate (3Yr CAGR)", "${res["eps_growth_cagr"]}%"),
                _buildProjectionRow("Current Earnings Per Share (EPS)", "₹${res["current_eps"]}"),
                _buildProjectionRow("3-Years Ago EPS", "₹${res["eps_3yr_ago"]}"),
                _buildProjectionRow("Projected 3-Year Future EPS", "₹${res["future_eps"]}"),
                _buildProjectionRow("Projected 3-Year Future Price", "₹${res["future_price"]}"),
                _buildProjectionRow("Required Return (Discount Rate)", "${res["required_return"]}%"),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricTile(String label, String value, IconData icon, Color valColor) {
    return Column(
      children: [
        Icon(icon, color: AppTheme.textSecondary, size: 20),
        const SizedBox(height: 6),
        Text(
          label,
          style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: valColor,
          ),
        ),
      ],
    );
  }

  Widget _buildProjectionRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
          Text(value, style: const TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.bold, fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildHistoryList() {
    if (_history.isEmpty) {
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 40.0),
        decoration: BoxDecoration(
          color: AppTheme.cardColor,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.borderGrey),
        ),
        child: const Center(
          child: Column(
            children: [
              Icon(Icons.history, color: AppTheme.textSecondary, size: 40),
              SizedBox(height: 12),
              Text(
                "No valuation logs found in Google Sheet.",
                style: TextStyle(color: AppTheme.textSecondary),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: _history.length,
      itemBuilder: (context, index) {
        final item = _history[index];
        final stockName = item["stock_name"] ?? "Unknown";
        final currentPrice = item["current_price"];
        final fairValue = item["fair_value"];
        final profit = item["profit"];
        
        final double? priceVal = double.tryParse(currentPrice.toString());
        final double? fairVal = double.tryParse(fairValue.toString());
        final isUndervalued = (fairVal != null && priceVal != null) ? fairVal > priceVal : false;
        final themeColor = isUndervalued ? AppTheme.neonGreen : AppTheme.neonRed;

        return Card(
          color: AppTheme.cardColor,
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: AppTheme.borderGrey),
          ),
          child: ListTile(
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            title: Text(
              stockName,
              style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
            ),
            subtitle: Padding(
              padding: const EdgeInsets.only(top: 4.0),
              child: Text(
                "Price: ₹$currentPrice  |  Fair Value: ₹$fairValue",
                style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
              ),
            ),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  "${double.tryParse(profit.toString())! >= 0 ? '+' : ''}₹$profit",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: themeColor,
                    fontSize: 15,
                  ),
                ),
                Text(
                  isUndervalued ? "Undervalued" : "Overvalued",
                  style: TextStyle(color: themeColor, fontSize: 10, fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
