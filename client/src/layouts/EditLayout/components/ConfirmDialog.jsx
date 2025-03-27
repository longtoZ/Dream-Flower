import React from 'react'

const ConfirmDialog = ({ message, onConfirm, onCancel, isOpen }) => {
    if (!isOpen) return null;
  
    return (
        <div className="fixed inset-0 flex items-center justify-center bg-[#0000006e]">
            <div className="bg-secondary p-6 rounded-lg shadow-lg">
                <div className="text-lg">{message}</div>
                <div className="flex justify-end mt-4">
                    <b
                        className='w-20 bg-transparent mx-1 rounded-md border border-2 border-primary text-xs text-center text-white p-2 cursor-pointer hover:bg-primary transition-all duration-100 ease'
                        onClick={onCancel}
                    >
                    No
                    </b>
                    <button
                        className="w-20 bg-zinc-300 mx-1 rounded-md border border-2 border-primary text-xs text-center text-black p-2 cursor-pointer hover:bg-zinc-400 transition-all duration-100 ease"
                        onClick={onConfirm}
                    >
                    Yes
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ConfirmDialog