import { FC } from 'react';
import { motion } from 'framer-motion';
import { IconType } from 'react-icons';
import { FiHome, FiUploadCloud, FiBarChart2, FiSettings, FiMenu, FiX } from 'react-icons/fi';
import { useUIStore } from '../../../stores/uiStore';

interface NavItemProps {
  icon: IconType;
  label: string;
  isActive?: boolean;
}

const NavItem: FC<NavItemProps> = ({ icon: Icon, label, isActive }) => (
  <a
    href="#"
    className={`flex items-center gap-4 p-3 rounded-lg transition-colors ${
      isActive
        ? 'bg-primary/20 text-text-primary'
        : 'text-text-secondary hover:bg-primary/10'
    }`}
  >
    <Icon className="text-2xl" />
    <span className="font-heading">{label}</span>
  </a>
);

export const Sidebar = () => {
  const { isSidebarOpen, toggleSidebar } = useUIStore((state) => ({
    isSidebarOpen: state.isSidebarOpen,
    toggleSidebar: state.actions.toggleSidebar,
  }));

  return (
    <motion.nav
      className="glass-card h-full p-4 flex flex-col"
      initial={{ width: isSidebarOpen ? 280 : 80 }}
      animate={{ width: isSidebarOpen ? 280 : 80 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        {isSidebarOpen && <h1 className="text-2xl font-cyber text-gradient">SampleMind</h1>}
        <button onClick={toggleSidebar} className="text-text-secondary hover:text-primary">
          {isSidebarOpen ? <FiX className="h-6 w-6" /> : <FiMenu className="h-6 w-6" />}
        </button>
      </div>

      {/* Navigation */}
      <div className="flex flex-col gap-2">
        {/* Dummy Nav Items */}
        <NavItem icon={FiHome} label="Dashboard" isActive />
        <NavItem icon={FiUploadCloud} label="Upload" />
        <NavItem icon={FiBarChart2} label="Analytics" />
        <NavItem icon={FiSettings} label="Settings" />
      </div>

      {/* Footer */}
      <div className="mt-auto">
        {/* User Profile */}
      </div>
    </motion.nav>
  );
};
