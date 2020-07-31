function [rall] = um3_mpc_data()
    load('20190222_chain.mat')
    % load('20190305_chain1.mat')
    
    %%
%     datbeg = 1050;datend = 5984;
    datbeg = 12553;datend = 13070; % end data
    % datbeg = 3260;datend = 4080;
    u = ultimaker_3_adi_global_c_target0(datbeg:datend)';
    y = ultimaker_3_adi_global_c_temperature0(datbeg:datend)';
    for i = 1:length(y)
        if y(i)>500
            y(i) = y(i-1);
        end
    end
    % plot(ADI_ELAPSED_TIME(datbeg:datend),u); hold on;
    % plot(ADI_ELAPSED_TIME(datbeg:datend),y);
    %
    tplot = 0:0.5:0.5*(datend-datbeg);
    tplot = tplot(:);
    data = iddata(y,u,0.5);
    [sys3,x0] = n4sid(data,2,'Form','canonical')
%     compare(data,sys2,sys3)


    %% simple MPC
    A = sys3.A;
    B = sys3.B;
    C = sys3.C;
    G = []; M = []; dly = 10;
    N = 50+dly;
    for i = 1:N
        nb = size(B,1);
        gi = [];
        for j = 1:i
            gi = [A^(j-1)*B gi];
        end
        gi = [gi zeros(nb,N-i)];
        G = [G;gi];
        M = [M;A^i];
    end
    Q = 10*eye(2);
    R = 1;
    [Pinf] = idare(A,B,Q,R,[],[]);
    Qbar = kron(eye(N-1),Q);
    Qbar = blkdiag(Qbar,Pinf);
    Rbar = kron(eye(N),R);
%     x0 = [120;120];
%     simlen = 4500;
    datbeg = 1050;datend = 5984;
    rall = ultimaker_3_adi_global_c_target0(datbeg:datend)';
    rvec = rall(1:N);
%     U = []; X = []; E = []; Y = [];
    % options =  optimset('Display','off');
    Aineq = toeplitz([-1;zeros(N-1,1)],[-1 1,zeros(1,N-2)]);
    Aineq = Aineq(1:end-1,:);
    bineq = 25*ones(size(Aineq,1),1);
    P = G'*Qbar*G+Rbar; 
    P = (P'+P)./2;
%     q = G'*Qbar*(M*x0-rvec);
    lb = 0*ones(size(q));
    ub = 220*ones(size(q));
    Aeq = [eye(dly),zeros(dly,N-dly)]; beq = zeros(dly,1);
%     Aeq = [zeros(21,29), eye(21)]; beq = zeros(21,1);
%     cycletimes = [];
    A_ss = [eye(2)-A -B; C 0]; Q_ss = 10*eye(3);
    A_ss_ineq = [0 0 1; 0 0 -1]; b_ss_ineq = [ub(1);-lb(1)];
save('mpcdat.mat','P','q','Aineq','bineq','lb','ub',...
    'A','B','C','M','G','Qbar','Rbar','N','rall','Aeq','beq',...
    'dly','A_ss','Q_ss','A_ss_ineq','b_ss_ineq');
end

% for i = 1:simlen  
%     tic;
%     soln = quadprog(P,q,Aineq,bineq,[],[],lb,ub,[],options);
% %     soln = quadprog(P,q,[],[],[],[],lb,ub,[],options);
%     uk = soln(1);
%     U = [U;uk];
%     xk = A*x0 + B*uk;
%     X = [X,xk];
%     yk = C*xk;
%     Y = [Y;yk];
%     E = [E;rvec(1)-yk];
%     % for next cycle
%     x0 = xk;
%     rvec = rall(i:i+N-1);
%     q = G'*Qbar*(M*x0-rvec);
%     cycletimes = [cycletimes;toc];
% end
% %
% plot(rall,':r','linewidth',1.2,'displayname','G-Code Ref');
% hold on;
% plot(Y,'b','linewidth',1.2,'displayname','Network Controller');
% sysout = y;
% plot(sysout,'--c','linewidth',1.2,'displayname','Local Controller');
% legend show

