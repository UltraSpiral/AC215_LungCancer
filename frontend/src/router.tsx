import { lazy, Suspense, useEffect, useState } from 'react';
import { ReviewPage } from './pages/ReviewPage';
import { inferenceMode } from './api';

const KitchenSink = lazy(() => import('./pages/KitchenSink').then((m) => ({ default: m.KitchenSink })));

/** Two routes only, so a pathname switch is enough — no router dependency. */
export function Router() {
  const [path, setPath] = useState(() => window.location.pathname);

  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  if (inferenceMode === 'mock' && path.replace(/\/$/, '') === '/kitchen-sink') {
    return (
      <Suspense fallback={null}>
        <KitchenSink />
      </Suspense>
    );
  }
  return <ReviewPage />;
}
