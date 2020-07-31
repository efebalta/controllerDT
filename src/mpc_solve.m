function [uk,xk,yk,q] = mpc_solve(rvec,x0)
    load('mpcdat.mat')
    options =  optimset('Display','off');
    soln = quadprog(P,q,Aineq,bineq,[],[],lb,ub,[],options);
%     soln = quadprog(P,q,[],[],[],[],lb,ub,[],options);
    uk = soln(1);
    xk = A*x0 + B*uk;
    yk = C*xk;
    % for next cycle
%     x0 = xk;
%     rvec = rall(i:i+N-1);
    q = G'*Qbar*(M*x0-rvec);
end