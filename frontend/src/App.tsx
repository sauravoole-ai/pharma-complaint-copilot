import { useEffect } from "react";

import { ComplaintWorkspace } from "./components/ComplaintWorkspace";
import { useAppDispatch } from "./store";
import { loadLedger } from "./store/complaintSlice";

export default function App() {
  const dispatch = useAppDispatch();
  useEffect(() => {
    void dispatch(loadLedger());
  }, [dispatch]);

  return <ComplaintWorkspace />;
}
