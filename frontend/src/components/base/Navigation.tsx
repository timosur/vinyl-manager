'use client';
import { useState, useEffect } from 'react';
import {
  Cog6ToothIcon,
  HomeIcon,
  CircleStackIcon,
  DocumentArrowUpIcon,
  MusicalNoteIcon,
} from '@heroicons/react/24/outline'

let navigation = [
  { name: 'Home', href: '/', icon: HomeIcon, current: false },
  { name: 'Releases', href: '/release', icon: CircleStackIcon, current: false },
  { name: 'Mixtape', href: '/mixtape', icon: MusicalNoteIcon, current: false },
  { name: 'Import', href: '/import', icon: DocumentArrowUpIcon, current: false },
];

const settingsLink = { href: '/settings', current: false };

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export const Navigation = () => {
  const [path, setPath] = useState('');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const currentPath = window.location.pathname;
      setPath(currentPath);
      settingsLink.current = currentPath.includes('/settings');
    }
  }, []);

  // Update the current state for navigation and teams
  navigation = navigation.map(item => ({
    ...item,
    current: item.href === path,
  }));


  return (
    <>
      {/* Static sidebar for desktop */}
      <div className="lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
        {/* Sidebar component, swap this element with another sidebar if you like */}
        <div
          className="flex grow flex-col gap-y-5 overflow-y-auto navigation-bar-background px-6 pb-4  bg-gradient-to-b">
          <div className="flex h-16 shrink-0 items-center">
              <span>Vinyl Manager</span>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <a
                        href={item.href}
                        className={classNames(
                          item.current
                            ? 'font-bold'
                            : 'font-semibold',
                          'group flex gap-x-3 rounded-md p-2 text-sm leading-6 '
                        )}
                      >
                        <item.icon
                          className={classNames(
                            'h-6 w-6 shrink-0'
                          )}
                          aria-hidden="true"
                        />
                        {item.name}
                      </a>
                    </li>
                  ))}
                </ul>
              </li>

              <li className="mt-auto">
                <a
                  href={settingsLink.href}
                  className={classNames(
                    'group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6'
                  )}
                >
                  <Cog6ToothIcon
                    className="h-6 w-6 shrink-0 group-hover:text-white"
                    aria-hidden="true"
                  />
                  Settings
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </div>


    </>
  )
}
