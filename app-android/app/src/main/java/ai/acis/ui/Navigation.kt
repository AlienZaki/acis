package ai.acis.ui

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import ai.acis.AcisViewModel

private data class NavItem(val route: String, val label: String, val icon: ImageVector)

private val NAV_ITEMS = listOf(
    NavItem("session",  "Session",  Icons.Default.Home),
    NavItem("history",  "History",  Icons.AutoMirrored.Filled.List),
    NavItem("settings", "Settings", Icons.Default.Settings),
)

@Composable
fun AcisNavHost(vm: AcisViewModel) {
    val navController = rememberNavController()
    val backStack by navController.currentBackStackEntryAsState()
    val current = backStack?.destination?.route ?: "session"
    val showBottomBar = !current.startsWith("sessionDetail")

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NavigationBar {
                    NAV_ITEMS.forEach { item ->
                        NavigationBarItem(
                            selected = current == item.route,
                            onClick = {
                                if (current != item.route) {
                                    navController.navigate(item.route) {
                                        popUpTo("session") { saveState = true }
                                        launchSingleTop = true
                                        restoreState = true
                                    }
                                }
                            },
                            icon = { Icon(item.icon, contentDescription = item.label) },
                            label = { Text(item.label) },
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(navController = navController, startDestination = "session") {
            composable("session") { SessionScreen(vm, innerPadding) }
            composable("history") {
                HistoryScreen(
                    vm = vm,
                    outerPadding = innerPadding,
                    onSessionClick = { sessionId ->
                        navController.navigate("sessionDetail/$sessionId")
                    },
                )
            }
            composable("settings") { SettingsScreen(vm, innerPadding) }
            composable(
                route = "sessionDetail/{sessionId}",
                arguments = listOf(navArgument("sessionId") { type = NavType.StringType }),
            ) { backStackEntry ->
                val sessionId = backStackEntry.arguments?.getString("sessionId") ?: return@composable
                SessionDetailScreen(
                    vm = vm,
                    sessionId = sessionId,
                    onBack = { navController.navigateUp() },
                )
            }
        }
    }
}
