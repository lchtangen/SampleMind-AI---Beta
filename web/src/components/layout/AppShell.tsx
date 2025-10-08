/**
 * AppShell Component
 * 
 * Main application shell that combines Navbar, Sidebar, and content area
 */

import { cn } from '@/lib/utils';
import { useAppStore } from '@/store/appStore';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

export function AppShell() {
    const sidebarOpen = useAppStore((state) => state.ui.sidebarOpen);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            {/* Animated background gradient */}
            <div className="fixed inset-0 bg-gradient-radial from-purple-900/10 via-transparent to-transparent gradient-shift" />
            <div className="fixed inset-0 bg-grid-white/[0.02]" />

            {/* Navigation */}
            <Navbar />

            {/* Sidebar */}
            <Sidebar />

            {/* Main Content */}
            <main
                className={cn(
                    'relative pt-16 transition-all duration-300',
                    sidebarOpen ? 'lg:pl-64' : 'lg:pl-20'
                )}
            >
                <div className="container mx-auto p-6">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}